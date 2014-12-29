#include <iostream>
#include <string>
#include <vector>

std::string evaluate(std::vector<std::string>& sequences)
{
        // TODO
        return "";
}

// Read DNA sequences from standard in, one per line.
//
// Write to standard out the longest subsequence that any two
// sequences have in common.
int main(int argc, char** argv)
{
        std::vector<std::string> sequences;
        while (!std::cin.eof())
        {
	        std::string input;
                std::cin >> input;
                sequences.push_back(input);
        }

        std::string result = evaluate(sequences);
        std::cout << result << std::endl;
        return 0;
}