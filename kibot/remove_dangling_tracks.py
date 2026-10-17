#!/usr/bin/env python3

import argparse
import sys

import pcbnew


def endpoint_is_dangling(connectivity, track, position):
    return connectivity.TestTrackEndpointDangling(track, False, position)


def board_tracks(board):
    tracks = board.Tracks()
    return [tracks[index] for index in range(len(tracks))]


def remove_dangling_tracks(board):
    board.BuildConnectivity()
    initial_connectivity = board.GetConnectivity()
    initial_unconnected = initial_connectivity.GetUnconnectedCount(False)
    removed = 0

    connectivity = board.GetConnectivity()
    dangling = []

    for track in board_tracks(board):
        if isinstance(track, pcbnew.PCB_VIA):
            continue

        if endpoint_is_dangling(connectivity, track, track.GetStart()) or endpoint_is_dangling(
            connectivity, track, track.GetEnd()
        ):
            dangling.append(track)

    for track in dangling:
        board.Remove(track)
        removed += 1

    board.BuildConnectivity()
    final_connectivity = board.GetConnectivity()
    final_unconnected = final_connectivity.GetUnconnectedCount(False)

    if final_unconnected > initial_unconnected:
        raise RuntimeError(
            "dangling-track cleanup increased unconnected items "
            f"from {initial_unconnected} to {final_unconnected}"
        )

    return removed, initial_unconnected, final_unconnected


def main():
    parser = argparse.ArgumentParser(
        description="Remove dead-end track branches without worsening connectivity"
    )
    parser.add_argument("input", help="input KiCad PCB")
    parser.add_argument("output", help="output KiCad PCB")
    args = parser.parse_args()

    board = pcbnew.LoadBoard(args.input)
    removed, initial_unconnected, final_unconnected = remove_dangling_tracks(board)

    if not pcbnew.SaveBoard(args.output, board):
        raise RuntimeError(f"failed to save cleaned board to {args.output}")

    print(f"removed_tracks={removed}")
    print(f"initial_unconnected={initial_unconnected}")
    print(f"final_unconnected={final_unconnected}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise
