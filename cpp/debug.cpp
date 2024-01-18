#include <iostream>
#include <vector>
#include "solver.cpp"


void print_probs(vector<vector<long double>>& probs) {
    const int height = probs.size();
    const int width = probs[0].size();
    for (int h = 0; h < height; ++h) {
        for (int w = 0; w < width; ++w){
            print((std::to_string(probs[h][w]) + ".00").substr(0, 4), "");
        }
        println();
    }
}

void print_cell_states(vector<vector<int>>& cell_states, vector<vector<long double>>& probs) {
    const int height = probs.size();
    const int width = probs[0].size();
    for (int h = 0; h < height; ++h) {
        for (int w = 0; w < width; ++w){
            if (cell_states[h][w] != -1) {
                print(cell_states[h][w]);
            } else if (probs[h][w] == 1.0) {
                print("@");
            } else if (probs[h][w] == 0.0) {
                print("#");
            } else {
                print("X");
            }
        }
        println();
    }
}

vector<vector<vector<int>>> test_cases = {
    {
        {0, 1, 1, 2, -1, 1, 0, 0, 0, 0, 1, -1, -1, -1, -1, -1},
        {0, 2, -1, 3, 1, 2, 2, 2, 1, 0, 1, -1, -1, -1, -1, -1},
        {0, 2, -1, 3, 1, 1, -1, -1, 1, 1, 2, -1, -1, -1, 2, 2},
        {0, 1, 3, -1, 2, 1, 2, 2, 2, 2, -1, 2, 1, 3, -1, 2},
        {0, 0, 2, -1, 3, 1, 1, 0, 1, -1, 3, 2, 0, 2, -1, 3},
        {0, 0, 1, 1, 2, -1, 2, 1, 1, 2, -1, 1, 0, 1, 2, -1},
        {1, 1, 0, 0, 2, 4, -1, 2, 0, 2, 2, 2, 0, 1, 2, 2},
        {-1, 2, 1, 1, 1, -1, -1, 2, 0, 1, -1, 1, 0, 1, -1, 1},
        {2, 3, -1, 1, 1, 2, 2, 1, 0, 1, 1, 1, 0, 1, 1, 1},
        {-1, 2, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0},
        {1, 1, 0, 0, 0, 0, 1, 1, 2, -1, 1, 1, 1, 1, 0, 0},
        {1, 2, 1, 1, 0, 0, 1, -1, 2, 1, 1, 1, -1, 1, 0, 0},
        {-1, 2, -1, 1, 0, 1, 3, 3, 2, 1, 1, 2, 1, 2, 1, 1},
        {1, 2, 1, 1, 0, 2, -1, -1, 3, 2, -1, 1, 0, 1, -1, 1},
        {0, 0, 0, 0, 0, 2, -1, -1, -1, -1, 2, 2, 1, 2, 2, 2},
        {0, 0, 0, 0, 0, 1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1}
    },
    {
        {-1, -1, 1, 0, 0, 0, 0, 0, 0},
        {-1, -1, 1, 0, 0, 0, 0, 0, 0},
        {-1, 2, 2, 1, 0, 0, 0, 0, 0},
        {-1, -1, -1, 2, 0, 0, 0, 0, 0},
        {1, 3, -1, 2, 0, 0, 0, 0, 0},
        {2, 3, 3, 2, 1, 0, 0, 0, 0},
        {-1, -1, 2, -1, 2, 1, 0, 0, 0},
        {2, 2, 2, 3, -1, 2, 0, 1, 1},
        {0, 0, 0, 2, -1, 2, 0, 1, -1}
    }
};

int main() {
    vector<vector<int>> cell_states = test_cases[1];
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    int n_bombs = width == 9 ? 10 : width == 16 ? 40 : 100;
    vector<vector<long double>> probs = calculate_prob(cell_states, n_bombs);
    print_probs(probs);
    print_cell_states(cell_states, probs);
}
