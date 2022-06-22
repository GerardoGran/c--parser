# The transition table is an array made up of dictionaries, allowing whichever character is being read to be used as a key to return the state it must move to.
# This file is used to generate that dictionary array based on a .csv file with the transition table.
# This is done to reduce time spent in a manual task, it has no effect on the final scanner software component.
import csv


def create_transition_table():
    transition_table = []

    # open file
    with open('util/transitions.csv', encoding='utf-8-sig') as csvfile:
        # create reader object named transitions
        transitions = csv.reader(csvfile, delimiter=',')

        # list to store column headers to become keys in our dicts
        keys = []

        # iterate over each row
        for i, row in enumerate(transitions):
            # store only first row as keys
            if i == 0:
                keys = row
                continue

            # dict from each state
            transition_dict = {}

            # j: index of key in keys list; state: the state to transition to
            for j, state in enumerate(row):
                # result: {'key': state}
                transition_dict[keys[j]] = int(state)

            # add dict to transition_table list
            transition_table.append(transition_dict)

        # print to copy and paste in scanner.py
        for d in transition_table:
            print(f"{d},")

    return transition_table
