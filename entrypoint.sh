#!/bin/bash
cd is_there_a_game/
# exec python3 -m game_process_calculator
uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8765
# uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8000
