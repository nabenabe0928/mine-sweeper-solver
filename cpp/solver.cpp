#include <iostream>
#include <vector>
#include <tuple>
#include <functional>

using std::vector;
using std::pair;
using std::function;
using std::tie;

typedef vector<int> vi1;
typedef vector<vi1> vi2;
typedef vector<bool> vb1;
typedef vector<vb1> vb2;
typedef vector<long double> vd1;
typedef vector<vd1> vd2;
typedef vector<pair<int, int>> vpi1;
typedef vector<vpi1> vpi2;
typedef vector<vpi2> vpi3;

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

// Math

void compute_combination(vd2& combination_memo){
    int n = combination_memo.size();
    for (int i = 0; i < n; ++i){
        combination_memo[i][0] = 1.0;
        for (int j = 1; j <= i; ++j){
            combination_memo[i][j] = combination_memo[i][j - 1] / j * (i + 1 - j);
        }
    }
}

void normalize_probs(vd1& probs, long double prob_sum) {
    for (auto& p: probs) {
        p /= prob_sum;
    }
}

// Count utilities

int count_close_around(vi2& cell_states, vpi1& neighbor_positions){
    int count = 0;
    for (const auto& [y, x]: neighbor_positions){
        if (cell_states[y][x] == -1){
            ++count;
        }
    }
    return count;
}

int count_open_around(vi2& cell_states, vpi1& neighbor_positions){
    int count = 0;
    for (const auto& [y, x]: neighbor_positions){
        if (cell_states[y][x] != -1){
            ++count;
        }
    }
    return count;
}

int count_bomb_around(vb2& bomb_cells, vpi1& neighbor_positions){
    int count = 0;
    for (const auto& [y, x]: neighbor_positions){
        if (bomb_cells[y][x]){
            ++count;
        }
    }
    return count;
}

int count_safe_around(vi2& cell_states, vb2& safe_cells, vpi1& neighbor_positions){
    int count = 0;
    for (const auto& [y, x]: neighbor_positions){
        if (safe_cells[y][x] || cell_states[y][x] != -1){
            ++count;
        }
    }
    return count;
}

int count_hard_cells(vi2& cell_states, vpi3& neighbor_list) {
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    int count = 0;
    for (int h = 0; h < height; ++h){
        for (int w = 0; w < width; ++w){
            if (cell_states[h][w] != -1){
                continue;
            }
            vpi1& neighbor_positions = neighbor_list[h][w];
            if (count_close_around(cell_states, neighbor_positions) == neighbor_positions.size()) {
                ++count;
            }
        }
    }
    return count;
}

int count_bombs(vb2& bomb_cells) {
    const int height = bomb_cells.size();
    const int width = bomb_cells[0].size();
    int count = 0;
    for (int h = 0; h < height; ++h){
        for (int w = 0; w < width; ++w){
            if (bomb_cells[h][w]) {
                ++count;
            }
        }
    }
    return count;
}

// Determine the initial state

vb2 determine_bomb_cells(vi2& cell_states, vpi3& neighbor_list){
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    vb2 bomb_cells = vb2(height, vb1(width, false));
    for (int h = 0; h < height; ++h){
        for (int w = 0; w < width; ++w){
            const int n_bombs_around = cell_states[h][w];
            if (cell_states[h][w] <= 0){
                continue;
            }
            vpi1& neighbor_positions = neighbor_list[h][w];
            int close_count = count_close_around(cell_states, neighbor_positions);
            if (close_count != n_bombs_around) {
                continue;
            }
            for (const auto& [y, x]: neighbor_positions){
                if (cell_states[y][x] == -1) {
                    bomb_cells[y][x] = true;
                }
            }
        }
    }
    return bomb_cells;
}

vb2 determine_safe_cells(vi2& cell_states, vpi3& neighbor_list, vb2& bomb_cells){
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    vb2 safe_cells = vb2(height, vb1(width, false));
    for (int h = 0; h < height; ++h){
        for (int w = 0; w < width; ++w){
            const int n_bombs_around = cell_states[h][w];
            if (cell_states[h][w] < 0){
                continue;
            }
            vpi1& neighbor_positions = neighbor_list[h][w];
            safe_cells[h][w] = true;  // This is an open cell, so it is safe.
            int n_determined_bombs = count_bomb_around(bomb_cells, neighbor_positions);
            if (n_bombs_around != n_determined_bombs){
                continue;
            }
            for (const auto& [y, x]: neighbor_positions){
                if (!bomb_cells[y][x]){
                    safe_cells[y][x] = true;
                }
            }
        }
    }
    return safe_cells;
}

vpi3 get_neighbor_list(int height, int width){
    vpi3 neighbor_list = vpi3(height, vpi2(width, vpi1()));
    for (int h = 0; h < height; ++h){
        for (int w = 0; w < width; ++w){
            for (int dy = -1; dy <= 1; ++dy){
                int ny = h + dy;
                if (ny < 0 || ny >= height){
                    continue;
                }
                for (int dx = -1; dx <= 1; ++dx){
                    int nx = w + dx;
                    if (nx < 0 || nx >= width || (ny == h && nx == w)){
                        continue;
                    }
                    neighbor_list[h][w].push_back(std::make_pair(ny, nx));
                }
            }
        }
    }
    return neighbor_list;
}

vpi1 collect_target_cell_positions(vi2& cell_states, vpi3& neighbor_list, vb2& bomb_cells, vb2& safe_cells){
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    vpi1 target_cell_positions = vpi1();
    for (int h = 0; h < height; ++h){
        for (int w = 0; w < width; ++w){
            if (
                cell_states[h][w] != -1 ||
                bomb_cells[h][w] ||
                safe_cells[h][w] ||
                count_open_around(cell_states, neighbor_list[h][w]) == 0
            ) {
                continue;
            }
            target_cell_positions.push_back(std::make_pair(h, w));
        }
    }
    return target_cell_positions;
}

bool is_assumption_valid(
    int h,
    int w,
    vi2& cell_states,
    vpi3& neighbor_list,
    vb2& bomb_cells,
    vb2& safe_cells,
    int n_total_bombs
){
    const int width = cell_states[0].size();
    for (const auto& [y, x]: neighbor_list[h][w]){
        if (cell_states[y][x] == -1) {
            continue;
        }
        vpi1& neighbor_positions = neighbor_list[y][x];
        int n_neighbors = neighbor_positions.size();
        int true_n_bombs_around = cell_states[y][x];
        int n_bombs_around = count_bomb_around(bomb_cells, neighbor_positions);
        int n_safe_around = count_safe_around(cell_states, safe_cells, neighbor_positions);
        if (n_bombs_around > true_n_bombs_around || n_neighbors - n_safe_around < true_n_bombs_around){
            return false;
        }
    }
    return true;
}

void compute_prob(
    vd2& combination_memo,
    vb2& bomb_cells,
    vpi1& target_cell_positions,
    int n_hard_cells,
    int n_defined_bombs,
    int n_total_bombs,
    vd1& probs,
    long double& prob_sum
){
    const int width = bomb_cells[0].size();
    // n_hard_cells >= n_total_bombs - n_defined_bombs
    long double prob = combination_memo[n_hard_cells][n_total_bombs - n_defined_bombs];
    int n_targets = target_cell_positions.size();
    for (int i = 0; i < n_targets; ++i){
        const auto& [h, w] = target_cell_positions[i];
        if (bomb_cells[h][w]) {
            probs[i] += prob;
        }
    }
    if (n_hard_cells >= 1 && n_total_bombs - n_defined_bombs > 0){
        // Probability for hard cells.
        probs[n_targets] += combination_memo[n_hard_cells - 1][n_total_bombs - n_defined_bombs - 1];
    }
    prob_sum += prob;
}

void depth_first_search(
    int target_index,
    vd2& combination_memo,
    vi2& cell_states,
    vb2& bomb_cells,
    vb2& safe_cells,
    vpi3& neighbor_list,
    vpi1& target_cell_positions,
    int n_defined_bombs,
    int n_total_bombs,
    int n_hard_cells,
    vd1& probs,
    long double& prob_sum
){
    int n_targets = target_cell_positions.size();

    if (n_targets == target_index) {
        compute_prob(
            combination_memo,
            bomb_cells,
            target_cell_positions,
            n_hard_cells,
            n_defined_bombs,
            n_total_bombs,
            probs,
            prob_sum
        );
        return;
    }
    const int width = bomb_cells[0].size();
    const auto& [h, w] = target_cell_positions[target_index];
    bomb_cells[h][w] = true;
    if (
        n_hard_cells >= n_total_bombs - n_defined_bombs - 1 &&
        n_defined_bombs + 1 <= n_total_bombs &&
        is_assumption_valid(h, w, cell_states, neighbor_list, bomb_cells, safe_cells, n_total_bombs)
    ){
        depth_first_search(
            target_index + 1,
            combination_memo,
            cell_states,
            bomb_cells,
            safe_cells,
            neighbor_list,
            target_cell_positions,
            n_defined_bombs + 1,
            n_total_bombs,
            n_hard_cells,
            probs,
            prob_sum
        );
    }
    bomb_cells[h][w] = false;
    safe_cells[h][w] = true;
    if (
        n_hard_cells >= n_total_bombs - n_defined_bombs &&
        n_defined_bombs <= n_total_bombs &&
        is_assumption_valid(h, w, cell_states, neighbor_list, bomb_cells, safe_cells, n_total_bombs)
    ){
        depth_first_search(
            target_index + 1,
            combination_memo,
            cell_states,
            bomb_cells,
            safe_cells,
            neighbor_list,
            target_cell_positions,
            n_defined_bombs,
            n_total_bombs,
            n_hard_cells,
            probs,
            prob_sum
        );
    }
    safe_cells[h][w] = false;
}

vd2 assign_probs(vd1& probs, vpi1& target_cell_positions, vi2& cell_states, vb2& bomb_cells, vb2& safe_cells){
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    vd2 prob_in_cells = vd2(height, vd1(width, -1.0));
    const int n_targets = target_cell_positions.size();
    for (int i = 0; i < n_targets; ++i) {
        const auto& [y, x] = target_cell_positions[i];
        prob_in_cells[y][x] = probs[i];
    }
    for (int h = 0; h < height; ++h) {
        for (int w = 0; w < width; ++w){
            if (prob_in_cells[h][w] >= 0) {
                continue;
            }
            if (safe_cells[h][w] || cell_states[h][w] != -1) {
                prob_in_cells[h][w] = 0.0;
            } else if (bomb_cells[h][w]) {
                prob_in_cells[h][w] = 1.0;
            } else {
                prob_in_cells[h][w] = probs[n_targets];
            }
        }
    }
    return prob_in_cells;
}

vd2 solve(vi2& cell_states, int n_total_bombs){
    const int height = cell_states.size();
    const int width = cell_states[0].size();
    vpi3 neighbor_list = get_neighbor_list(height, width);
    vb2 bomb_cells = determine_bomb_cells(cell_states, neighbor_list);
    vb2 safe_cells = determine_safe_cells(cell_states, neighbor_list, bomb_cells);
    vpi1 target_cell_positions = collect_target_cell_positions(cell_states, neighbor_list, bomb_cells, safe_cells);
    vd2 combination_memo = vd2(width * height + 1, vd1(width * height + 1, 0.0));
    vd1 probs = vd1(target_cell_positions.size() + 1, 0.0);
    compute_combination(combination_memo);
    int n_hard_cells = count_hard_cells(cell_states, neighbor_list);
    long double prob_sum = 0.0;
    depth_first_search(
        0,
        combination_memo,
        cell_states,
        bomb_cells,
        safe_cells,
        neighbor_list,
        target_cell_positions,
        count_bombs(bomb_cells),
        n_total_bombs,
        n_hard_cells,
        probs,
        prob_sum
    );
    normalize_probs(probs, prob_sum);
    return assign_probs(probs, target_cell_positions, cell_states, bomb_cells, safe_cells);
}

int main(){
    // https://github.com/nabenabe0928/mine-sweeper-solver/blob/main/demodata/medium14/demo012.png
    vi2 cell_states = {
        {-1, -1, -1, -1, -1, -1, -1, -1, 2, 1, 1, -1, 1, 0, 1, -1},
        {-1, -1, -1, -1, -1, 2, -1, -1, -1, 2, 1, 2, 2, 1, 1, 1},
        {-1, -1, -1, -1, -1, 1, 1, 3, -1, 2, 0, 2, -1, 2, 0, 0},
        {-1, -1, -1, -1, -1, 2, 2, 2, 1, 1, 0, 2, -1, 3, 1, 0},
        {-1, -1, -1, -1, -1, -1, -1, 1, 1, 2, 2, 2, 2, -1, 2, 1},
        {-1, -1, -1, -1, -1, 3, 2, 1, 1, -1, -1, 1, 1, 2, -1, 1},
        {-1, -1, -1, -1, -1, 2, 1, 0, 1, 2, 2, 1, 0, 1, 1, 1},
        {-1, -1, -1, -1, -1, -1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {-1, -1, -1, -1, -1, -1, 2, 0, 0, 0, 0, 0, 1, 1, 1, 0},
        {-1, -1, -1, -1, -1, 3, 3, 2, 1, 1, 1, 1, 1, -1, 1, 0},
        {-1, -1, -1, -1, -1, 2, -1, -1, 2, 2, -1, 1, 1, 1, 1, 0},
        {-1, -1, -1, -1, -1, 3, 3, 2, 2, -1, 2, 1, 1, 1, 2, 1},
        {-1, -1, -1, -1, -1, -1, 1, 0, 1, 1, 1, 1, 2, -1, 2, -1},
        {-1, -1, -1, -1, -1, 2, 3, 1, 1, 0, 0, 1, -1, 2, 2, 1},
        {-1, -1, -1, -1, -1, -1, 2, -1, 1, 1, 1, 2, 1, 1, 0, 0},
        {-1, -1, -1, -1, -1, 1, 2, 1, 1, 1, -1, 1, 0, 0, 0, 0},
    };
    vd2 probs = solve(cell_states, 40);
    const int height = probs.size();
    const int width = probs[0].size();
    for (int h = 0; h < height; ++h) {
        for (int w = 0; w < width; ++w){
            print((std::to_string(probs[h][w]) + ".00").substr(0, 4), "");
        }
        println();
    }
}
