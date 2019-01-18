# The Traits Database Project

## All right, what's this all about then?
**Challenge**: Extract trait information from unstructured or semi-structured natural history notations. That is, if I'm given text like:

 ```This rather large female specimen is 12 lbs 7 oz and 3 feet 7 inches in total length.```

 I should be able to extract:

 - sex = female
 - body mass = 5,641 g
 - total length = 1,092 mm


 Of course this is a rather straight-forward example. Natural history/museum notations are highly idiosyncratic and may use various shorthand notations. Here are just a few examples of how total length measurements appear:

 - `Total Length: 15.7cm`
 - `15.7cm T.L.`
 - `157-60-20-19=21g`
 - `SVL 157 mm`
 - `standard length: 157-215mm`
 - `t.l.= 2 feet 3.1 - 4.5 inches`
 - As well as measurements embedded in prose like: `Snout vent lengths range anywhere from 16 to 23 cm.` I am experimenting with various distances between the anchor token `Snout vent lengths` and the measurements `16 to 23 cm`.
 - We flag ambiguous measurements like: `length: 12.0`. This may be a total length measurement or another length measurement.
 - We also flag numeric measurements without units like: `total length = 120`. The units may be the default millimeters.
 - etc.

Values from controlled vocabularies are also extracted.
 - These values sometimes have a signifier like `Life Stage: Adult`
 - And other times we see a value on its own like `Adult` without the signifier.

## Parsing strategy

Note that I am trying to extract data from text and not parse a formal language. Most importantly, I don't need to worry about recursive structures and the characters in the text can take on different meaning depending on the form. For is instance, in the form `15.7cm T.L.` the dot is used as both a decimal point and as an abbreviation indicator. Elsewhere, it is usually noise. This problem gets even more pronounced when words have multiple meanings like the letter "T" on its own. One some contexts it indicates a tail length measurement and in other contexts it indicates a testes notation.

Also note that we want to parse gigabytes (or terabytes) of data in relatively short amount of time. Speed isn't the primary concern but having fast turnaround is still important.

This implementation is using a technique that I call **"Stacked Regular Expressions"**. The concept is very simple:

1. Tokenize the text analogous to this method in the python `re` module documentation, [Writing a Tokenizer](https://docs.python.org/3/library/re.html#writing-a-tokenizer).

  So the following regular expressions will replace the regular expressions with the "sex", "word", "keyword", and "quest" tokens respectively.

  ```
  self.kwd('keyword', 'sex')
  self.kwd('sex', r' females? | males? | f | m')
  self.lit('word', r' \b [a-z] \S+ ')
  self.lit('quest', r' \? ')
  ```

  The tokenizer will elide over anything that is not recognized in one of the regular expressions. This greatly simplifies parsing.

- Use regular expressions to combine groups of tokens into a single token. Repeat this step until there is nothing left to combine.

  The following regular expression will replace the "non fully descended" or "abdominal non descended" sequence of tokens with the "state" token.

  ```
  self.replace('state', 'non fully descended | abdominal non descended')
  ```

- Use regular expressions to find patterns of tokens to extract into traits. This is a single pass.

  Here's a rule for recognizing when a sex. The first argument is a pointer to the function that will do the conversion. Traits may be converted in several ways.

  ```
  self.product(
      self.convert,
      r"""  keyword (?P<value> (?: sex | word ) quest )
          | keyword (?P<value> sex | word )""")
```

However, there are still issues with context that are not easily resolved with LL(k) or LR(k) parsing techniques. For example, the "T" abbreviation is used for both testes notations and tail length notations. Or the double quote '"' is used as both an abbreviation for inches and as a, well, quote character. A human can human can easily tell the difference but these parsers struggle. Ultimately, a machine learning or hybrid of machine learning and parsers approach may work better.

Some of the other techniques that I tried include:

- The original version used lists of regular expressions for parsing. As a proof-of-concept it was OK but ultimately proved too cumbersome to use. One of the problems with the regular expression only technique is the multiple meanings for certain characters or words as mentioned above. I was playing Whack-a-Mole with subtle parser bugs.

- I tried using Flex and Bison. This didn't work because there was not enough look-ahead in the parser for our needs.

- I tried writing my own shift-reduce parser. The resulting Python code was slow and the parsers began to become very *ad hoc*.

- I also tried to use a parser combinator library (`pyparsing`) which was a vast improvement in developer time and code clarity but ballooned the run-time by two orders of magnitude.

## List of traits extracted (so far)
- Body body mass
- Total length (aka snout vent length, fork length, etc.)
- Sex
- Life stage
- Testes state
- Testes size
- Tail Length
- Hind foot Length
- Ear Length


## Install

You will need to have Python3 installed, as well as pip, a package manager for python. You can install the requirements into your python environment like so:
```
git clone https://github.com/rafelafrance/traiter.git
python3 -m pip install --user -r traiter/requirements.txt
```

## Run
```
python3 traiter.py ... TODO ...
```
## Running tests
You will need to install `pytest`. After that, you can run the tests like so:
```
python -m pytest tests/
```
