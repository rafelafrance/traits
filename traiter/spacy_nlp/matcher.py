"""Common logic for parsing trait notations."""

from collections import defaultdict

from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
from spacy.util import filter_spans


class SpacyMatcher:
    """Shared parser logic."""

    def __init__(self, nlp=None):
        self.nlp = nlp
        self.matchers = defaultdict(list)  # Patterns to match at each step
        self.actions = {}                  # Action to take on a matched trait
        self.count = 0                     # Allow matchers with same label

    def add_terms(self, terms, step='terms'):
        """Add phrase matchers.

        Each term is a dict with at least these three fields:
            1) attribute: what spacy token field are we matching (ex. LOWER)
            2) label: what is the term's hypernym (ex. color)
            3) pattern: the phrase being matched (ex. gray-blue)
        """
        by_attr = defaultdict(list)

        for pattern in [t for t in terms]:
            by_attr[pattern['attr']].append(pattern)

        for attr, patterns in by_attr.items():
            matcher = PhraseMatcher(self.nlp.vocab, attr=attr)
            self.matchers[step].append(matcher)

            by_label = defaultdict(list)
            for term in terms:
                by_label[term['label']].append(term)

            for label, term_list in by_label.items():
                phrases = [self.nlp.make_doc(t['pattern']) for t in term_list]
                matcher.add(label, phrases)

    def add_patterns(self, matchers, step):
        """Build matchers that recognize traits and labels."""
        rules = self.step_rules(matchers, step)
        if not rules:
            return

        matcher = Matcher(self.nlp.vocab)
        self.matchers[step].append(matcher)
        for rule in rules:
            self.count += 1
            label = f"{rule['label']}.{self.count}"
            patterns = rule['patterns']
            matcher.add(label, patterns)
            if on_match := rule.get('on_match'):
                self.actions[label] = on_match

        return rules

    @staticmethod
    def step_rules(matchers, step):
        """Get all patterns for a step."""
        rules = []
        for matcher in matchers:
            rules += matcher.get(step, [])
        return rules

    @staticmethod
    def filter_matches(matches):
        """Filter a sequence of matches so they don't contain overlaps.

        Matches: array of tuples: [(match_id, start, end), ...]
        """
        if not matches:
            return []
        first, *rest = sorted(matches, key=lambda m: (m[1], -m[2]))
        cleaned = [first]
        for match in rest:
            if match[1] >= cleaned[-1][2]:
                cleaned.append(match)
        return cleaned

    def scan(self, doc, matchers, step):
        """Find all terms in the text and return the resulting doc."""
        matches = []

        for matcher in matchers:
            matches += matcher(doc)

        spans = [Span(doc, s, e, label=i) for i, s, e in matches]
        spans = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in spans:
                label = span.label_
                action = self.actions.get(label)
                data = action(span) if action else {}
                if data.get('_forget'):
                    continue
                label = label.split('.')[0]
                label = data['_relabel'] if data.get('_relabel') else label
                attrs = {'ENT_TYPE': label, '_': {'data': data, 'step': step}}
                retokenizer.merge(span, attrs=attrs)

        return doc

    def __call__(self, doc):
        """Parse the doc in steps, building up a full parse in steps."""
        for step, matchers in self.matchers.items():
            doc = self.scan(doc, self.matchers[step], step=step)

            # print(step)
            # for token in doc:
            #     print(f'{token.ent_type_:<15} {token.pos_:<6} '
            #           f'{token.lemma_} => {token}')
            # print()

        return doc