#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <cstdlib>
#include <chrono>
#include <sstream>
#include <time.h>
#include <unordered_set>
#include "VertexColouring.h"
/*
n m

10 4
1 2
2 3
3 4
1 4


*/

struct FlatGraph {
	std::vector<int> offset;
	std::vector<int> neighbours;
	int n;
	int max_degree;
};

//Input: Adjacency list representation of graph, number of nodes/edges
//Output: FlatGraph struct with all data in 2 'static' arrays
FlatGraph flatten(std::vector<std::vector<int>>& G, int n, int m) {
	FlatGraph fg = { std::vector<int>(n + 1), std::vector<int>(2 * m) , n, INT_MIN };
	
	int accum = 0;
	for (int i = 0; i < n; i++) {
		fg.offset[i] = accum;
		accum += G[i].size();
		if (G[i].size() > fg.max_degree) {
			fg.max_degree = G[i].size();
		}
	}
	fg.offset[n] = accum;


	int i = 0;
	for (std::vector<int>& v : G) {
		for (int& x : v) {
			fg.neighbours[i++] = x;
		}
	}

	return fg;
}

//Uses greedy coloring like: https://en.wikipedia.org/wiki/Greedy_coloring with randomized order
//Input: Graph
//Output: List of integers assigning vertex i with color output[i]
std::vector<int> greedy_color(FlatGraph& fg) {
	std::vector<int> color(fg.n, -1);
	std::vector<int> order(fg.n);
	generate(order.begin(), order.end(), [ind = 0]() mutable {return ind++; });
	std::srand(time(NULL));
	std::random_shuffle(order.begin(), order.end());
	std::vector<int> colors_nearby;
	for (int vertex : order) {
		int count = fg.offset[vertex + 1] - fg.offset[vertex];
		if (count == 0) {
			color[vertex] = 0;
		}
		else {
			//minimal color available in neighbourhood
			//Remark: using a set for more efficiency is not faster, runs at best factor ~5 SLOWER...
			colors_nearby.resize(count);
			generate(colors_nearby.begin(), colors_nearby.end(),
				[ind = fg.offset[vertex], &fg, &color]() mutable { return color[fg.neighbours[ind++]]; });
			int col = 0;
			while (find(colors_nearby.begin(), colors_nearby.end(), col) != colors_nearby.end()) {
				col++;
			}
			color[vertex] = col;
		}
	}
	return color;
}

// Input: Graph and color assignment
// Output: True if color is unique in neighbourhood for all vertices, false otherwise
bool verify_coloring(FlatGraph& fg, std::vector<int>& color) {

	for (int i = 0; i < fg.n; i++) {
		int col = color[i];
		for (int j = fg.offset[i]; j < fg.offset[i + 1]; j++) {
			if (col == color[fg.neighbours[j]]) {
				return false;
			}
		}
	}

	return true;
}

void populate_from_file_simple(const char* file_name, std::vector<std::vector<int>>& G) {
	FILE* in = fopen(file_name, "r");
	int x, y;
	int i = 0;
	fscanf(in, "%d %d", &x, &y); //Discard first line
	while (fscanf(in, "%d %d", &x, &y) != EOF) {
		G[x].push_back(y);
		G[y].push_back(x);
		i++;
	}
	fclose(in);
	std::cout << "[SIMPLE] Read " << i << " value pairs." << std::endl;
}

const int BUFFER_SIZE = 8192*64;
// adapted from answer by Mats Petersson on stackoverflow:
// https://stackoverflow.com/questions/15115943/what-is-the-best-efficient-way-to-read-millions-of-integers-separated-by-lines-f
void populate_from_file_fast(const char* file_name, std::vector<std::vector<int>>& G) {
	int num = 0;
	int last = -1;
	FILE* f = fopen(file_name, "r");
	int x, y;
	fscanf(f, "%d %d", &x, &y); //Discard first line
	char buffer[BUFFER_SIZE];
	int i = 0;
	int bytes = 0;
	char* p;
	int hasnum = 0;
	int eof = 0;
	while (!eof){
		memset(buffer, 13, sizeof(buffer));  // To detect end of files.
		fread(buffer, 1, sizeof(buffer), f);
		p = buffer;
		bytes = sizeof(buffer);// BUFFER_SIZE;
		while (bytes > 0){
			if (*p == 13){ //eof marker
				eof = 1;
				break;
			}
			if (*p == '\n' || *p == ' '){
				if (hasnum) {
					if (last < 0) {
						last = num;
					}
					else {
						G[last].push_back(num);
						G[num].push_back(last);
						i++;
						last = -1;
					}
				}
				num = 0;
				p++;
				bytes--;
				hasnum = 0;
			}else if (*p >= '0' && *p <= '9'){
				hasnum = 1;
				num *= 10;
				num += *p - '0';
				p++;
				bytes--;
			}else{
				std::cout << "Error in reading file fast... *p = " << (int)*p << " i= " << i << std::endl;
				exit(1);
			}
		} 
	}
	std::cout << "[FAST] Read " << i << " value pairs" << std::endl;
	fclose(f);
}

//Function wrapper, compiler was complaining, didn't understand error well enough to fix
void f(int argc, char* argv[]) {
	auto start = std::chrono::high_resolution_clock::now();
	const char* file_name_in;
	const char* file_name_out;
	if (argc == 3) {
		file_name_in = argv[1];
		file_name_out = argv[2];
	}
	else {
		std::cout << "not enough cmd arguments, using in.txt/out.txt" << std::endl;
		file_name_in = "in.txt";
		file_name_out = "out.txt";
	}
	int x, y;
	FILE* in = fopen(file_name_in, "r");
	fscanf(in, "%d %d", &x, &y);
	fclose(in);

	int n = x, m = y;
	x = y = 0;
	//G[vertex] = {neigh_1, ..., neigh_n}
	std::vector<std::vector<int>> G(n, std::vector<int>());
	populate_from_file_fast(file_name_in, G);
	//populate_from_file_simple(file_name_in, G);
	auto stop = std::chrono::high_resolution_clock::now();
	std::cout << "Done reading " << m << " lines in "
		<< std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count()
		<< " ms." << std::endl;
	start = std::chrono::high_resolution_clock::now();

	FlatGraph fg = flatten(G, n, m);

	stop = std::chrono::high_resolution_clock::now();
	std::cout << "Done flattening in "
		<< std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count()
		<< " ms." << std::endl;

	//Free memory
	for (auto& v : G) {
		v.resize(0);
		v.shrink_to_fit();
	}
	G.resize(0);
	G.shrink_to_fit();

	std::vector<int> color(n);
	//Num of trials
	int k = 10000;
	int teller = 0;
	int best = INT_MAX;
	while (teller++ < k) {
		auto substart = std::chrono::high_resolution_clock::now();
		std::vector<int> _color = greedy_color(fg);
		int max = *std::max_element(_color.begin(), _color.end());
		if (max < best) {
			best = max;
			std::cout << "Found new best: " << best+1 << "\n";
			std::copy(_color.begin(), _color.end(), color.begin());
		}
		auto substop = std::chrono::high_resolution_clock::now();
		std::cout << teller << ": " << std::chrono::duration_cast<std::chrono::milliseconds>(substop - substart).count() << " ms." << std::endl;
	}
	stop = std::chrono::high_resolution_clock::now();
	std::cout << "Done coloring " << k << " random orders in "
		<< std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count()
		<< " ms." << std::endl;

	start = std::chrono::high_resolution_clock::now();

	std::stringstream ss;
	ss << "[";

	for (int i = 0; i < color.size() - 1; i++) {
		ss << color[i];
		ss << ", ";
	}
	ss << color.back();
	ss << "]";
	ss << "\n";
	const std::string tmp = ss.str();
	const char* cstr = tmp.c_str();
	FILE* out = fopen(file_name_out, "w");
	fprintf(out, cstr);
	//std::cout << cstr << std::endl;
	stop = std::chrono::high_resolution_clock::now();
	std::cout << "Done writing in " << std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count() << " ms." << std::endl;
	int max = (*std::max_element(color.begin(), color.end()) + 1);
	std::cout << max << " colors used." << std::endl;

	bool color_valid = verify_coloring(fg, color);

	if (color_valid) {
		std::cout << "Coloring valid." << std::endl;
	}
	else {
		std::cout << "Coloring not valid." << std::endl;
	}

	return;
}

//Program entry
int main(int argc, char* argv[])
{
	f(argc, argv);
	return 0;
}