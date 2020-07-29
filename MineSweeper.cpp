#include <bits/stdc++.h>
using namespace std;

std::mt19937 create_rand_engine(){
    std::random_device rnd;
    std::vector<std::uint_least32_t> v(10);
    std::generate(v.begin(), v.end(), std::ref(rnd));
    std::seed_seq seed(v.begin(), v.end());
    return std::mt19937(seed);
}

vector<int> generate_unique_array(const size_t sz, int start, int end){
    const size_t range = static_cast<size_t>(start - end + 1);
    const size_t num = static_cast<size_t>(sz * 1.2);

    vector<int> ret;
    auto engine = create_rand_engine();
    std::uniform_int_distribution<int> distribution(start, end);

    while (ret.size() < sz){
        while (ret.size() < num) ret.push_back(distribution(engine));
        sort(ret.begin(), ret.end());
        auto unique_end = unique(ret.begin(), ret.end());

        if (sz < distance(ret.begin(), unique_end)){
            unique_end = next(ret.begin(), sz);
        }

        ret.erase(unique_end, ret.end());
    }

    return ret;
}

struct MineSweeper{
    int W, H, B, Difficulty, n_closed;
    vector<int> field, cell;
    bool clear, over;

    MineSweeper(int diff){
        Difficulty = diff;
        W = vector<int>({9, 16, 30})[diff];
        H = vector<int>({9, 16, 16})[diff];
        B = vector<int>({10, 40, 100})[diff];
        n_closed = W * H;
        field = vector<int>(W * H, 0);
        cell = vector<int>(W * H, -1);
        clear = over = false;
    }

    int _position_to_num(int x, int y){
        return y * W + x;
    }

    int GetCellInfo(int x, int y){
        return cell[_position_to_num(x, y)];
    }

    pair<int, int> _num_to_position(int num){
        return make_pair(num % W, num / W);
    }

    bool out_of_field(int x, int y){
        if (x < 0 || x >= W) return true;
        if (y < 0 || y >= H) return true;
        return false;
    }

    void _print_result(){
        if (over){
            cout << "*******************" << endl;
            cout << "***  game over  ***" << endl;
            cout << "*******************\n" << endl;
        }else if (clear){
            cout << "*********************" << endl;
            cout << "***  game clear!  ***" << endl;
            cout << "*********************\n" << endl;
        }
    }

    void _plot_field(){
        _print_result();
        for (int y = 0; y < H; y++){
            for (int x = 0; x < W; x++){
                int num = _position_to_num(x, y);
                if (cell[num] == -1){
                    cout << "x ";
                }else if (field[num] >= 0 && cell[num] >= 0){
                    cout << GetCellInfo(x, y) << " ";
                }else{
                    cout << "@ ";
                }
            }
            cout << "" << endl;
        }
        cout << "" << endl;
    }

    void open(int x, int y){
        int num = _position_to_num(x, y);
        cell[num] = field[num];
        n_closed--;
        if (cell[num] == -2) over = true;

        queue<pair<int, int>> q;
        q.push({x, y});
        while (!q.empty()){
            
        }
        /*
        BFS Here
        */

        if (n_closed == B) clear = true;
        _plot_field();
    }

    vector<int> _get_neighbors(int x, int y){
        vector<int> neighbors;
        for (int dx = -1; dx <= 1; dx++){
            for (int dy = -1; dy <= 1; dy++){
                if (!out_of_field(x + dx, y + dy))
                    neighbors.push_back(_position_to_num(x + dx, y + dy));
            }
        }
        return neighbors;
    }

    vector<int> _fill_bombs(vector<int>& not_here){
        vector<int> bombs, rnd = generate_unique_array(B + 10, 0, W * H - 1);
        for (int i = 0; bombs.size() < B; i++){
            bool ok = true;
            for (int n: not_here){
                if (n == rnd[i]){
                    ok = false;
                    break;
                }
            }
            if (ok) bombs.push_back(rnd[i]);
        }
        return bombs;
    }

    int _bomb_count(int x, int y){
        vector<int> neighbors = _get_neighbors(x, y);
        int num = _position_to_num(x, y);
        if (field[num] == -2) return -2;

        int count = 0;
        for (int neighbor: neighbors){
            if (num == neighbor) continue;
            if (field[neighbor] == -2) count++;
        }
        return count;
    }

    void _initialize_field(vector<int>& bombs){
        for (int b: bombs) field[b] = -2;
        for (int x = 0; x < W; x++){
            for (int y = 0; y < H; y++){
                field[_position_to_num(x, y)] = _bomb_count(x, y);
            }
        }

        for (int x = 0; x < W; x++){
            for (int y = 0; y < H; y++){
                field[_position_to_num(x, y)] = _bomb_count(x, y);
            }
        }
    }

    void start(int x, int y){
        vector<int> neighbors = _get_neighbors(x, y);
        vector<int> bombs = _fill_bombs(neighbors);
        _initialize_field(bombs);
        open(x, y);
    }
};

int main(void){
    MineSweeper m(2);
    m.start(5, 5);

    return 0;
}
