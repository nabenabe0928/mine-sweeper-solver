cmake_minimum_required(VERSION 3.11)  # FetchContent is available in 3.11+
set(CMAKE_CXX_STANDARD 17)
project(mine_sweeper_solver)

include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.6.1
)
FetchContent_MakeAvailable(pybind11)

pybind11_add_module(mine_sweeper_solver cpp/solver_wrapper.cpp)
