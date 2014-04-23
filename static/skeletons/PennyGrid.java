import java.util.*;
import java.io.*;

class PennyGrid {

	public int evaluate(int[][] board) {
		// TODO
		return -1;
	}

	/**
	 * Accepts input from standard input and writes result to standard
	 * output.
	 *
	 * The first two lines of input will be single numbers that
	 * define the number of rows and columns. Each subsequent line
	 * will represent one row of the chessboard, with the number
	 * of pennies in each cell separated by spaces.
	 *
	 * For example the input:
	 *
	 * 4
	 * 4
	 * 2 2 4 2
	 * 0 3 0 1
	 * 1 2 2 1
	 * 4 1 2 2
	 *
	 * Should print to standard output:
	 *
	 * 15
	 */
	public static void main(String args[]) throws IOException {
		// You should not need to modify this method
		BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
		int nrows = Integer.parseInt(reader.readLine());
		int ncols = Integer.parseInt(reader.readLine());

		int[][] board = new int[nrows][];
		for (int row = 0 ; row < nrows ; row++) {
			board[row] = new int[ncols];
			String line = reader.readLine();
			String[] split = line.split(" ");
			for (int col = 0 ; col < ncols ; col++) {
				board[row][col] = Integer.parseInt(split[col]);
			}
		}

		int result = new PennyGrid().evaluate(board);
		System.out.println(result);
	}

}
