import java.util.*;
import java.io.*;

class DnaSequences {

	public String evaluate(List<String> sequences) {
		// TODO
		return "";
	}

	/**
	 * Read DNA sequences from standard in, one per line.
	 *
	 * Write to standard out the longest subsequence that any two
	 * sequences have in common.
	 *
	 */
	public static void main(String args[]) throws IOException {
		BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
		List<String> sequences = new ArrayList<String>();
		String line;
		while((line = reader.readLine()) != null) {
			sequences.add(line);
		}

		String result = new DnaSequences().evaluate(sequences);
		System.out.println(result);
	}

}
