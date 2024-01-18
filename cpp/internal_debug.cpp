#include <iostream>
#include <vector>

using std::vector;
using std::pair;

void print(){}
void println(){std::cout << std::endl;}
template <class Head, class... Tail>
void print(Head&& head, Tail&&... tail){std::cout << head; if (sizeof...(tail) != 0) std::cout << " "; print(std::forward<Tail>(tail)...);}
template <class T>
void print(vector<T>& vs){for (auto v: vs){std::cout << v; if (&v != &vs.back()) std::cout << " ";} std::cout << std::endl;}
template <class Head, class... Tail>
void println(Head&& head, Tail&&... tail){std::cout << head; if (sizeof...(tail) != 0) std::cout << " "; println(std::forward<Tail>(tail)...);}
template <class T>
void println(vector<T>& vs){for (auto v: vs) std::cout << v << std::endl;}

void print_cell_def(vector<pair<int, int>>& target_cell_positions, vector<vector<int>>& cell_definitions) {
    for (const auto& [h, w]: target_cell_positions) {
        print(cell_definitions[h][w]);
    }
    println();
}
