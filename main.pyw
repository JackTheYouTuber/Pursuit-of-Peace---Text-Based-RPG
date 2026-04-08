import traceback
import tkinter as tk
from tkinter import messagebox
from app.app import App
from app.logger import GameLogger


if __name__ == "__main__":
    logger = GameLogger()
    error_msg = None
    try:
        game = App(logger=logger)
        game.run()
    except Exception as e:
        error_msg = traceback.format_exc()
        logger.error(error_msg)
        # Show popup – create a temporary root if needed
        root = tk.Tk()
        root.withdraw()  # hide the main window
        messagebox.showerror(
            "Pursuit of Peace – Critical Error",
            f"The game encountered an unexpected error and will close.\n\n"
            f"Details:\n{str(e)}\n\n"
            f"Check the log file for more information."
        )
        root.destroy()
        raise  # re-raise so the script exits with error code