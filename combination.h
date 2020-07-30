#include <bits/stdc++.h>
using namespace std;

struct CombinationMemo{
    vector<vector<double>> memo;

    CombinationMemo(){}

    void build(int sz){
        memo = vector<vector<double>>(sz + 1, vector<double>(sz + 1, 0));
        memo[0][0] = 1;
        for (int i = 1; i < sz + 1; i++){
            for (int j = 0; j < i + 1; j++){
                memo[i][j] += memo[i - 1][j];
                if (j > 0) memo[i][j] += memo[i - 1][j - 1];
            }
        }
    }

    double nCk(int n, int k){
        if (n == k && n == 0) return 1;
        else if (n <= 0 || k < 0 || k > n) return 0;
        return memo[n][k];
    }
};
