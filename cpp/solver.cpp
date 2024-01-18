#include <vector>

using std::vector;
using std::pair;

struct AssumptionDefinition {
    const int bomb = 0;
    const int safe = 1;
    const int undefined = -1;
};

const AssumptionDefinition assumption_definition = AssumptionDefinition();
const int closed_cell_state = -1;

vector<vector<long double>> compute_combination(int n){
    vector<vector<long double>> combination_memo = vector<vector<long double>>(n, vector<long double>(n, 0.0));
    for (int i = 0; i < n; ++i){
        combination_memo[i][0] = 1.0;
        for (int j = 1; j <= i; ++j){
            combination_memo[i][j] = combination_memo[i][j - 1] / j * (i + 1 - j);
        }
    }
    return combination_memo;
}

struct MineSweeperSolver {
    // constant variables.
    const vector<vector<int>> cell_states;
    const int n_total_bombs;
    const int height;
    const int width;
    vector<vector<vector<pair<int, int>>>> neighbor_list;
    int n_hard_cells;
    int n_initial_bombs;
    int n_targets;
    vector<vector<long double>> combination_memo;
    vector<pair<int, int>> target_cell_positions;

    // state variables.
    vector<vector<int>> cell_definitions;

    // variables for the result.
    vector<long double> probs;
    long double prob_sum;

    MineSweeperSolver(vector<vector<int>>& cell_states, int n_total_bombs) :
        cell_states(cell_states),
        n_total_bombs(n_total_bombs),
        height(cell_states.size()),
        width(cell_states[0].size())
    {
        neighbor_list = get_neighbor_list();
        cell_definitions = vector<vector<int>>(height, vector<int>(width, -1));
        determine_bomb_cells();
        determine_safe_cells();
        target_cell_positions = collect_target_cell_positions();
        n_targets = target_cell_positions.size();
        combination_memo = compute_combination(width * height + 1);
        probs = vector<long double>(target_cell_positions.size() + 1, 0.0);
        n_hard_cells = count_hard_cells();
        n_initial_bombs = count_bombs();
        prob_sum = 0.0;
    }

    bool is_safe(int h, int w) {
        return cell_definitions[h][w] == assumption_definition.safe;
    }
    
    bool is_bomb(int h, int w) {
        return cell_definitions[h][w] == assumption_definition.bomb;
    }

    bool is_closed(int h, int w) {
        return cell_states[h][w] == closed_cell_state;
    }

    int count_close_around(vector<pair<int, int>>& neighbor_positions){
        int count = 0;
        for (const auto& [y, x]: neighbor_positions){
            if (is_closed(y, x)){
                ++count;
            }
        }
        return count;
    }

    int count_open_around(vector<pair<int, int>>& neighbor_positions){
        return (int) neighbor_positions.size() - count_close_around(neighbor_positions);
    }

    int count_bomb_around(vector<pair<int, int>>& neighbor_positions){
        int count = 0;
        for (const auto& [y, x]: neighbor_positions){
            if (is_bomb(y, x)){
                ++count;
            }
        }
        return count;
    }

    int count_safe_around(vector<pair<int, int>>& neighbor_positions){
        int count = 0;
        for (const auto& [y, x]: neighbor_positions){
            if (is_safe(y, x)){
                ++count;
            }
        }
        return count;
    }

    int count_bombs() {
        int count = 0;
        for (int h = 0; h < height; ++h){
            for (int w = 0; w < width; ++w){
                if (is_bomb(h, w)) {
                    ++count;
                }
            }
        }
        return count;
    }

    int count_hard_cells() {
        int count = 0;
        for (int h = 0; h < height; ++h){
            for (int w = 0; w < width; ++w){
                if (!is_closed(h, w)){
                    continue;
                }
                vector<pair<int, int>>& neighbor_positions = neighbor_list[h][w];
                if (count_close_around(neighbor_positions) == (int) neighbor_positions.size()) {
                    ++count;
                }
            }
        }
        return count;
    }

    void determine_bomb_cells(){
        for (int h = 0; h < height; ++h){
            for (int w = 0; w < width; ++w){
                const int n_bombs_around = cell_states[h][w];
                if (is_closed(h, w) || cell_states[h][w] == 0){
                    continue;
                }
                vector<pair<int, int>>& neighbor_positions = neighbor_list[h][w];
                int close_count = count_close_around(neighbor_positions);
                if (close_count != n_bombs_around) {
                    continue;
                }
                for (const auto& [y, x]: neighbor_positions){
                    if (is_closed(y, x)) {
                        cell_definitions[y][x] = assumption_definition.bomb;
                    }
                }
            }
        }
    }

    void determine_safe_cells(){
        for (int h = 0; h < height; ++h){
            for (int w = 0; w < width; ++w){
                const int n_bombs_around = cell_states[h][w];
                if (is_closed(h, w)){
                    continue;
                }
                vector<pair<int, int>>& neighbor_positions = neighbor_list[h][w];
                cell_definitions[h][w] = assumption_definition.safe;  // This is an open cell, so it is safe.
                int n_determined_bombs = count_bomb_around(neighbor_positions);
                if (n_bombs_around != n_determined_bombs){
                    continue;
                }
                for (const auto& [y, x]: neighbor_positions){
                    if (!is_bomb(y, x)){
                        cell_definitions[y][x] = assumption_definition.safe;
                    }
                }
            }
        }
    }

    vector<vector<vector<pair<int, int>>>> get_neighbor_list(){
        vector<vector<vector<pair<int, int>>>> neighbor_list = vector<vector<vector<pair<int, int>>>>(
            height, vector<vector<pair<int, int>>>(
                width, vector<pair<int, int>>()
            )
        );
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

    vector<pair<int, int>> collect_target_cell_positions(){
        vector<pair<int, int>> target_cell_positions = vector<pair<int, int>>();
        for (int h = 0; h < height; ++h){
            for (int w = 0; w < width; ++w){
                if (
                    cell_definitions[h][w] != assumption_definition.undefined ||
                    count_open_around(neighbor_list[h][w]) == 0
                ) {
                    continue;
                }
                target_cell_positions.push_back(std::make_pair(h, w));
            }
        }
        return target_cell_positions;
    }

    bool is_assumption_valid(int h, int w, int n_defined_bombs, int n_undefined_cells) {
        if (n_hard_cells + n_undefined_cells < n_total_bombs - n_defined_bombs || n_defined_bombs > n_total_bombs) {
            return false;
        }

        for (const auto& [y, x]: neighbor_list[h][w]){
            if (is_closed(y, x)) {
                continue;
            }
            vector<pair<int, int>>& neighbor_positions = neighbor_list[y][x];
            int n_neighbors = neighbor_positions.size();
            int true_n_bombs_around = cell_states[y][x];
            int n_bombs_around = count_bomb_around(neighbor_positions);
            int n_safe_around = count_safe_around(neighbor_positions);
            if (n_bombs_around > true_n_bombs_around || n_neighbors - n_safe_around < true_n_bombs_around){
                return false;
            }
        }
        return true;
    }

    void compute_prob(int n_defined_bombs) {
        // n_hard_cells >= n_total_bombs - n_defined_bombs
        long double prob = combination_memo[n_hard_cells][n_total_bombs - n_defined_bombs];
        for (int i = 0; i < n_targets; ++i){
            const auto& [h, w] = target_cell_positions[i];
            if (is_bomb(h, w)) {
                probs[i] += prob;
            }
        }
        if (n_hard_cells >= 1 && n_total_bombs - n_defined_bombs > 0){
            // Probability for hard cells.
            probs[n_targets] += combination_memo[n_hard_cells - 1][n_total_bombs - n_defined_bombs - 1];
        }
        prob_sum += prob;
    }

    void depth_first_search(int target_index, int n_defined_bombs) {
        if (n_targets == target_index) {
            compute_prob(n_defined_bombs);
            return;
        }
        const auto& [h, w] = target_cell_positions[target_index];
        cell_definitions[h][w] = assumption_definition.bomb;
        int n_undefined_cells = n_targets - target_index - 1;
        if (is_assumption_valid(h, w, n_defined_bombs + 1, n_undefined_cells)){
            depth_first_search(target_index + 1, n_defined_bombs + 1);
        }
        cell_definitions[h][w] = assumption_definition.safe;
        if (is_assumption_valid(h, w, n_defined_bombs, n_undefined_cells)) {
            depth_first_search(target_index + 1, n_defined_bombs);
        }
        cell_definitions[h][w] = assumption_definition.undefined;
    }

    vector<vector<long double>> get_probs(){
        vector<vector<long double>> prob_in_cells = vector<vector<long double>>(
            height, vector<long double>(width, -1.0)
        );
        for (auto& p: probs) {
            p /= prob_sum;
        }
        for (int i = 0; i < n_targets; ++i) {
            const auto& [y, x] = target_cell_positions[i];
            prob_in_cells[y][x] = probs[i];
        }
        for (int h = 0; h < height; ++h) {
            for (int w = 0; w < width; ++w){
                if (prob_in_cells[h][w] >= 0) {
                    continue;
                }
                if (is_safe(h, w)) {
                    prob_in_cells[h][w] = 0.0;
                } else if (is_bomb(h, w)) {
                    prob_in_cells[h][w] = 1.0;
                } else {
                    prob_in_cells[h][w] = probs[n_targets];
                }
            }
        }
        return prob_in_cells;
    }

    vector<vector<long double>> solve() {
        depth_first_search(0, n_initial_bombs);
        return get_probs();    
    }
};

vector<vector<long double>> calculate_prob(vector<vector<int>>& cell_states, int n_total_bombs){
    MineSweeperSolver solver = MineSweeperSolver(cell_states, n_total_bombs);
    return solver.solve();
}
