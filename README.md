# Evolution Simulator

This project simulates many cubes trying to get to randomly appearing food items of different value, varying in:
  1- Speed (affects how quickly they move and their food required to surive)
  2- Greed (determines how they prioritize food size compared to food distance)
  3- Size (affects how large the cube is and their food required to survive) 

Each generation, the cube that did the best creates future cubes that are all similar to it (+/-20% in each trait). This repeats indefinitely.

To run this project, run 'main.py' with PyGame running on Python3.
