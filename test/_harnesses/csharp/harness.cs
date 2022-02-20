using System;
using System.Collections.Generic;

class TestHarness {

    static private bool OK = true;
    static protected void softAssert(bool condition, string label)
    {
        if (!condition)
        {
            Console.Error.WriteLine("FAILED! CSharp: " + label);
            OK = false;
        }
    }

    static protected void check()
    {
        if (!OK)
        {
            Console.Error.WriteLine("Failed assertions.");
            Environment.Exit(1);
        }
    }

    // super basic, just turn it into dict please; don't want another dependency
    static protected Dictionary<string, string> parseArguments(string[] args)
    {
        Dictionary<string, string> parsed = new Dictionary<string, string>();

        string currentKeyword = null;
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i].StartsWith("--"))
            {
                currentKeyword = args[i].Substring(2);
                continue;
            }
            if (currentKeyword != null)
            {
                parsed[currentKeyword] = args[i];
                currentKeyword = null;
                continue;
            }
            // shouldn't get here in current usage
            parsed[args[i]] = "";
        }

        return parsed;
    }
}
