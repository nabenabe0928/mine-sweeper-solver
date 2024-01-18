#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "solver.cpp"


PYBIND11_MODULE(mine_sweeper_solver, m) {
  m.def("calculate_probability", &calculate_prob, "A function to calculate probabilities for the Minesweeper game");
}
