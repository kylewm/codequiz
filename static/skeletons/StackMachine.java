import java.util.*;
import java.io.*;

class StackMachine {

	public int evaluate(String input) {
		System.out.println(input);
		// TODO
		return -1;
	}

	/**
	 * Receives input on a single line from standard in. Computes
	 * and prints the result on a single line to standard out. For
	 * example, the input
	 *
	 * 11+2*
	 * 
	 * should yield the result:
	 * 
	 * 4
	 */
	public static void main(String args[]) throws IOException {
		BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

		String input = reader.readLine();
		int result = new StackMachine().evaluate(input);
		System.out.println(result);
	}
	
}
