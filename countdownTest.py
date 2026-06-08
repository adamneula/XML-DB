import time
import sys

def execute_with_countdown(seconds=5):
    print("WARNING: About to run a destructive data operation (Overwriting Database).")
    try:
        for i in range(seconds, 0, -1):
            # \r forces the terminal to overwrite the current line
            print(f"\rExecuting in {i} seconds... (Press Ctrl+C to ABORT) ", end="")
            time.sleep(1)
            
        print("\nCountdown complete. Executing function...")
        # --> YOUR SENSITIVE FUNCTION CALL GOES HERE <--
        
    except KeyboardInterrupt:
        # Catches the Ctrl+C so the script dies cleanly instead of throwing a massive traceback
        print("\n\nABORTED: Sensitive function canceled by user.")
        sys.exit(0)

# Call it before your execution
execute_with_countdown(5)
print("boom")