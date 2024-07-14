import argparse
import concurrent.futures
import os
import sys
from datetime import datetime
from functools import partial
from typing import List

import requests

from activities import ACTIVITIES

USER_AGENT = "export-tool"
DEBUG = False


def main(token: str, path: str) -> None:
    start_time = datetime.now()
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return
    print("Listing workouts...")
    workouts: List[dict] = list_workouts(token)
    print("Exporting workouts...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        callable = partial(export_workout, token, path)
        results_future = executor.map(callable, workouts)
    results = list(results_future)
    succeeded = len(list(filter(lambda x: x is True, results)))
    failed = len(list(filter(lambda x: x is False, results)))
    exec_time = datetime.now() - start_time
    print(
        f"\nFinished exporting workouts in {exec_time}. {succeeded} workouts successfully exported, {failed} failed."
    )


def list_workouts(token: str) -> List[dict]:
    url = "https://api.sports-tracker.com/apiserver/v1/workouts"
    params = {"limited": "true", "limit": "1000000"}
    headers = {"STTAuthorization": token, "User-Agent": USER_AGENT}
    data = requests.get(url, params=params, headers=headers, timeout=120).json()
    # Expected data shape is {"error": None, "payload": list of workout dicts, "metadata": {"workoutcount": count, "until": timestamp}}
    if data["error"] is not None:
        raise Exception(f"Workout listing failed: {data['error']}")
    return data["payload"]


def export_workout(token: str, path: str, workout: dict) -> bool:
    workout_key = workout["workoutKey"]
    activity_id = workout["activityId"]
    activity_name = ACTIVITIES[activity_id]
    start_time_ms = workout["startTime"]
    start_time_str = datetime.fromtimestamp(start_time_ms / 1000).strftime(
        "%Y-%m-%dT%H_%M_%S"
    )
    file_name = f"{start_time_str}_{activity_name}.gpx"
    file_path = os.path.join(path, file_name)
    try:
        url = f"https://api.sports-tracker.com/apiserver/v1/workout/exportGpx/{workout_key}"
        headers = {"User-Agent": USER_AGENT}
        params = {"token": token}
        response = requests.get(url, params=params, headers=headers, timeout=120)
        with open(file_path, "w") as f:
            f.write(response.text)
        sys.stdout.write(".")
        sys.stdout.flush()
        return True
    except Exception:
        print(f"\nExporting workoutKey {workout_key} failed!")
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="Authentication token (get from STTAuthorization header)",
    )
    parser.add_argument(
        "--export-path",
        type=str,
        required=True,
        help="Folder path to save exported workouts",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.token, args.export_path)
