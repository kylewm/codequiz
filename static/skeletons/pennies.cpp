#include <iostream>

int evaluate(int** grid, int nrows, int ncolumns)
{
	// TODO
	return -1;
}

// Accepts input from standard input and writes result to standard
// output.
//
// The first two lines of input will be single numbers that define the
// number of rows and columns. Each subsequent line will represent one
// row of the grid, with the number of pennies at each tile separated
// by spaces.
//
// For example the input:
//
// 4
// 4
// 2 2 4 2
// 0 3 0 1
// 1 2 2 1
// 4 1 2 2
//
// Should print to standard output:
//
// 15
//
int main(int argc, char** argv)
{
	int nrows = 0, ncols = 0;

	std::cin >> nrows;
	std::cin >> ncols;

	int** arr = new int*[nrows];

	for (int row = 0 ; row < nrows ; row++) {
		arr[row] = new int[ncols];
		for (int col = 0 ; col < ncols ; col++) {
			std::cin >> arr[row][col];
		}
	}

	int result = evaluate(arr, nrows, ncols);
	std::cout << result << std::endl;

	for (int row = 0 ; row < nrows ; row++) {
		delete[] arr[row];
	}
	delete[] arr;

	return 0;
}
