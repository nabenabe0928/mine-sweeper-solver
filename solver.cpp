#include <bits/stdc++.h>
#include "MineSweeper.h"
#include "combination.h"
using namespace std;

template <typename A, typename B>
string to_string(pair<A, B> p);
template <typename A, typename B, typename C>
string to_string(tuple<A, B, C> p);
template <typename A, typename B, typename C, typename D>
string to_string(tuple<A, B, C, D> p);
string to_string(const string& s) {return '"' + s + '"';}
string to_string(char c){return string(1, c);}
string to_string(const char* s) {return to_string((string) s);}
string to_string(bool b){return (b ? "true" : "false");}
template <typename A, typename B>
string to_string(pair<A, B> p){return "(" + to_string(p.first) + ", " + to_string(p.second) + ")";}
template <typename A, typename B, typename C>
string to_string(tuple<A, B, C> p){return "(" + to_string(get<0>(p)) + ", " + to_string(get<1>(p)) + ", " + to_string(get<2>(p)) + ")";}
template <typename A, typename B, typename C, typename D>
string to_string(tuple<A, B, C, D> p){return "(" + to_string(get<0>(p)) + ", " + to_string(get<1>(p)) + ", " + to_string(get<2>(p)) + ", " + to_string(get<3>(p)) + ")";}
string to_string(vector<bool> v) {
  bool first = true;
  string res = "{";
  for (int i = 0; i < static_cast<int>(v.size()); i++) {
    if (!first) res += ", ";
    first = false;
    res += to_string(v[i]);
  }
  res += "}";
  return res;
}

template <size_t N>
string to_string(bitset<N> v) {
  string res = "";
  for (size_t i = 0; i < N; i++) res += static_cast<char>('0' + v[i]);
  return res;
}

template <typename A>
string to_string(A v) {
    bool first = true;
    string res = "{";
    for (const auto &x : v) {
        if (!first) {
            res += ", ";
        }
        first = false;
        res += to_string(x);
    }
    res += "}";
    return res;
}

template<typename T>
string to_string(priority_queue<T>& q){
    priority_queue<T> copy;
    bool first = true;
    string res = "{";
    while(!q.empty()){
        if (!first) {
            res += ", ";
        }
        first = false;
        res += to_string(q.top());
        copy.push(q.top());
        q.pop();
    }

    swap(q, copy);
    res += "}";
    return res;
}

void debug_out() {cerr << endl;}

template <typename Head, typename... Tail>
void debug_out(Head H, Tail... T){
    cerr << " " << to_string(H);
    debug_out(T...);
}

#define debug(...) cerr << "[" << #__VA_ARGS__ << "]:", debug_out(__VA_ARGS__)

struct Game{
    MineSweeper player;
    int W, H, n_Flag;
    double total;
    vector<vector<int>> each_neighbors;
    vector<bool> Flag, Safe, done;
    vector<int> closed;
    vector<double> probabilities;
    CombinationMemo comb;

    Game(MineSweeper player, CombinationMemo comb): player(player), comb(comb){
        W = player.W;
        H = player.H;
        n_Flag = 0;
        Flag = Safe = done = vector<bool>(W * H, false);
        closed = vector<int>(W * H);
        probabilities = vector<double>(W * H, 0);
        each_neighbors = player.each_neighbors;
    }

    bool _open_safe_neighbors(int x, int y, vector<int>& cell, vector<bool>& flag, vector<bool>& safe){
        int count = 0;
        int num = player._position_to_num(x, y);
        for (int neighbor: each_neighbors[num])
            if (flag[neighbor]) count++;

        bool opened = false;
        if (count == cell[num]){
            for (int neighbor: each_neighbors[num]){
                int x2, y2;
                tie(x2, y2) = player._num_to_position(neighbor);
                if (!flag[neighbor] && cell[neighbor] == -1)
                    safe[neighbor] = true, opened = true;
            }
        }
        return opened;
    }

    bool OpenSafe(){
        bool opened = false;
        for (int x = 0; x < W; x++){
            for (int y = 0; y < H; y++)
                if (player.GetCellInfo(x, y) != -1)
                    opened = opened | _open_safe_neighbors(x, y, player.cell, Flag, Safe);
        }
        return opened;
    }

    bool contradiction(int num, vector<bool>& flag, vector<bool>& safe){
        for (int neighbor: each_neighbors[num]){
            int n_bombs = player.cell[neighbor];
            if (done[neighbor] || n_bombs == -1) continue;
            int n_safe = 0, n_flag = 0, n_cells = each_neighbors[neighbor].size();
            for (int neighbor: each_neighbors[neighbor]){
                if (safe[neighbor]) n_safe++;
                if (flag[neighbor]) n_flag++;
            }
            if (n_flag > n_bombs || n_cells - n_safe < n_bombs) return true;
        }

        return false;
    }

    void _compute_probability(int idx, int n_target, int n_surrounded, int n_flags,
                              vector<bool>& flag, vector<bool>& safe){
        if (idx >= 1 && contradiction(closed[idx - 1], flag, safe)) return;
        if (idx == n_target){
            int rest = player.B - n_flags;
            if (n_surrounded < rest) return;

            double n_bomb_assignment_target = comb.nCk(n_surrounded, rest);
            double n_bomb_assignment_surrounded = comb.nCk(n_surrounded - 1, rest);
            total += n_bomb_assignment_target;
            for (int i = 0; i < W * H; i++)
                if (!flag[i] && safe[i])
                    probabilities[i] += n_bomb_assignment_target;
                else if (!flag[i] && !safe[i])
                    probabilities[i] += n_bomb_assignment_surrounded;
            return;
        }

        int num = closed[idx];
        flag[num] = true;
        if (n_flags < player.B)
            _compute_probability(idx + 1, n_target, n_surrounded, n_flags + 1, flag, safe);
        flag[num] = false;
        safe[num] = true;
        _compute_probability(idx + 1, n_target, n_surrounded, n_flags, flag, safe);
        safe[num] = false;
    }

    bool isSurrounded(int num){
        for (int neighbor: each_neighbors[num])
            if (player.cell[neighbor] != -1)
                return false;
        return true;
    }

    void open_high_probability(){
        queue<int> q;
        int num = 0; double M = 0;
        for (int i = 0; i < W * H; i++){
            probabilities[i] /= total;
            if (player.cell[i] == -1 && probabilities[i] > 1 - 1e-6)
                q.push(i);
            else if (player.cell[i] == -1 && M < probabilities[i])
                M = probabilities[i], num = i;
        }

        int x, y;
        if (q.empty()){
            tie(x, y) = player._num_to_position(num);
            player.open(x, y);
        }

        while (!q.empty()){
            tie(x, y) = player._num_to_position(q.front());
            q.pop();
            player.open(x, y);
        }
    }

    void open_by_probabilities(){
        vector<bool> flag_sim = Flag, safe_sim = Safe;
        fill(probabilities.begin(), probabilities.end(), 0);
        total = 0;
        int n_target = 0, n_surrounded = 0;
        for (int i = 0; i < W * H; i++)
            if (player.cell[i] == -1 && !Flag[i]){
                if (isSurrounded(i)) n_surrounded++;
                else closed[n_target++] = i;
        }
        _compute_probability(0, n_target, n_surrounded, n_Flag, flag_sim, safe_sim);
        open_high_probability();
        debug(probabilities);
        debug(n_surrounded);
        debug(n_target);
        debug(n_Flag);
        assert(probabilities[0] < 1.1);
    }

    void update(){
        for (int i = 0; i < W * H; i++){
            if (done[i] || player.cell[i] == -1)
                continue;
            int count = 0;
            for (int neighbor: each_neighbors[i])
                if (player.cell[neighbor] == -1) count++;
            if (player.cell[i] == count){
                done[i] = true;
                for (int neighbor: each_neighbors[i])
                    if (player.cell[neighbor] == -1)
                        Flag[neighbor] = true;
                    else
                        Safe[neighbor] = true;
            }
        }
        n_Flag = accumulate(Flag.begin(), Flag.end(), 0);
    }

    bool start(){
        player.start(W / 2, H / 2);

        while (!player.over && !player.clear){
            update();
            if (!OpenSafe()){
                open_by_probabilities();
            }else{
                for (int i = 0; i < W * H; i++){
                    int x, y;
                    tie(x, y) = player._num_to_position(i);
                    if (Safe[i]) player.open(x, y);
                }
            }
        }

        return !player.over;
    }
};

int main(void){
    int n_win = 0, n_game = 20, difficulty = 2;
    CombinationMemo comb;
    
    int t = clock();
    for (int i = 0; i < n_game; i++){
        MineSweeper player = MineSweeper(difficulty);
        if (i == 0) comb.build(player.W * player.H);
        Game game(player, comb);
        n_win += game.start();
        cout << i + 1 << ": " << "winning " << n_win << "\n" <<endl;
    }

    double rate = 100.0 * double(n_win) / double(n_game);
    cout << "winning rate: " << rate << " %" << endl;
    cout << "Elapsed Time: " << (clock() - t) / CLOCKS_PER_SEC << " [s]" << endl;
    return 0;
}
