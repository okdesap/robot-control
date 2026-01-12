"""
Command Queue Manager
Purpose
-------
- Accept commands quickly via REST without blocking the request.
- Execute commands sequentially in a dedicated worker thread.
- Provide status information (busy/idle, current job, queue length, last error).
- Support "emergency stop": cancel current command + clear queue.

This module MUST NOT import ROS or robot backends directly.
It stays in the core layer and is controlled by the Controller.
"""


import queue
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from collections.abc import Callable


@dataclass(frozen=True)
class QueuedCommand:
    """A command waiting in the queue(or currently executing)."""
    id: str
    command_text: str
    timestamp: float

@dataclass
class QueueStatus:
    state: str = "idle"  # "idle" | "busy" | "stopped"
    queue_length: int = 0

    current_id: str | None = None
    current_command: str | None = None
    current_timestamp: float | None = None

    processed_count: int = 0
    last_error: str | None = None
    last_completed_timestamp: float | None = None

class CommandQueueManager:
    """
    Producer/Consumer  queue manager with a single worker thread.

    Requires two callables:
      - execute_fn(command_text, cancel_event): executes ONE command
      - stop_fn(): immediate stop for the robot (used for emergency stop)

    The queue manager handles:
      - ordering (FIFO)
      - threading
      - status tracking
      - cancellation requests (via cancel_event)
    """
    def __init__(
        self,
        execute_fn: Callable[[str, threading.Event], None],
        stop_fn: Callable[[], None],
        max_queue_size: int = 40,
    ) -> None:
        self._execute_fn = execute_fn
        self._stop_fn = stop_fn

        self._queue: queue.Queue[QueuedCommand] = queue.Queue(maxsize=max_queue_size)
        self._status = QueueStatus()
        self._status_lock = threading.RLock()

        self._worker_thread = threading.Thread | None = None
        self._shutdown_event = threading.Event()
        self._cancel_current_event = threading.Event()

    def start(self) -> None:
        """Start the background thread if not already running."""
        with self._status_lock:
            if self._worker_thread is not None and self._worker_thread.is_alive():
                return  # Already running

            self._shutdown_event.clear()

            # Start the worker thread
            self._worker_thread = threading.Thread(
                target=self._worker_loop, 
                name="CommandQueueWorker", 
                daemon=True)
            self._worker_thread.start()

    def shutdown(self, timeout_s: float = 2.0) -> None:
        """Stop the worker thread gracefully.
        Also cancels any running command and clears the queue.
        """
        # First, stop robot motion and cancel current command
        self.emergency_stop(clear_queue=True)

        # Signal the worker loop to exit
        self._shutdown_event.set()

        # Wait briefly for the thread to finish
        if self._worker_thread:
            self._worker_thread.join(timeout=timeout_s)

        # Update status to reflect that processing has stopped
        with self._status_lock:
            self._status.state = "stopped"

    def enqueue(self, command_text: str) -> str:
        """Add a new command to the queue.
        Returns the unique command ID.
        Raises queue.Full if the queue is full.
        """
        cmd_id = str(uuid.uuid4())
        queued_cmd = QueuedCommand(
            id=cmd_id,
            command_text=command_text,
            timestamp=time.time()
        )
        #put into queue
        self._queue.put_nowait(queued_cmd)

        #update status
        with self._status_lock:
            self._status.queue_length = self._queue.qsize()
            if self._status.state == "stopped":
                self._status.state = "idle"

        return cmd_id
    
    def emergency_stop(self, clear_queue: bool = True) -> None:
        """Immediately stop the robot and cancel current command.
        Optionally clear the command queue.
        """
        # cancel current command
        self._cancel_current_event.set()

        # clear pending commands if requested
        if clear_queue:
            self._drain_queue()

        # stop robot immediately
        try:
            self._stop_fn()
        except Exception as e:
            with self._status_lock:
                self._status.last_error = f"stop_fn failed: {e}"
   

        # Update status
        with self._status_lock:
            self._status.queue_length = self._queue.qsize()
            if self._status.current_id is None and self._status.state != "stopped":
                self._status.state = "idle"
    
    def get_status(self) -> dict:
        """Return current status as a dictionary."""
        with self._status_lock:
            self._status.queue_length = self._queue.qsize()
            return asdict(self._status)
        
    def _drain_queue(self) -> None:
        """Remove all pending commands from the queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break
    
    def _worker_loop(self) -> None:
        """Background worker thread loop.
        - Waits for commands in the queue.
        - Executes them sequentially.(FIFO)
        - Updates status information.
        - Respects shutdown and cancellation events."""
        while not self._shutdown_event.is_set():
            try:
                # Wait for the next command
                queued_cmd = self._queue.get(timeout=0.5)
            except queue.Empty:
                with self._status_lock:
                    if self._status.current_id is None and self._status.state != "stopped":
                        self._status.state = "idle"
                        self._status.queue_length = self._queue.qsize()
                continue  # Check shutdown_event again

            # Update status to busy
            with self._status_lock:
                self._status.state = "busy"
                self._status.current_id = queued_cmd.id
                self._status.current_command = queued_cmd.command_text
                self._status.current_timestamp = time.time()
                self._status.queue_length = self._queue.qsize()

            # Clear cancel event before executing
            self._cancel_current_event.clear()

            # Execute the command
            try:
                self._execute_fn(queued_cmd.command_text, self._cancel_current_event)
    
                with self._status_lock:
                    self._status.processed_count += 1
                    self._status.last_completed_timestamp = time.time()
                    self._status.last_error = None
            except Exception as e:
                with self._status_lock:
                    self._status.last_error = f"execute_fn failed: {e}"

            finally:
                self._queue.task_done()

            # clear current command info
            with self._status_lock:
                self._status.current_id = None
                self._status.current_command = None
                self._status.current_timestamp = None
                self._status.queue_length = self._queue.qsize()

                if self._queue.qsize() == 0 and not self._shutdown_event.is_set():
                    self._status.state = "idle"