"""Actions for enriching entities with new data."""

from spacy import registry
from spacy.language import Language
from spacy.tokens import Doc

from traiter.actions import RejectMatch
from traiter.pipes.entity_data import EntityData, EntityPatterns
from traiter.util import as_list

ADD_ENTITY_DATA = 'add_entity_data'


@Language.factory(ADD_ENTITY_DATA)
class AddEntityData(EntityData):
    """Perform actions to fill user defined fields etc. for all entities."""

    def __init__(self, nlp: Language, name: str, patterns: EntityPatterns):
        super().__init__()
        self.nlp = nlp
        self.name = name
        self.dispatch = {p['label']: registry.misc.get(on) for p in as_list(patterns)
                         if (on := p.get('on_match'))}

    def __call__(self, doc: Doc) -> Doc:
        entities = []

        for ent in doc.ents:
            label = ent.label_

            if action := self.dispatch.get(label):
                try:
                    action(ent)
                except RejectMatch:
                    continue

                ent, label = self.relabel_entity(ent, label)

            ent._.data['trait'] = label
            ent._.data['start'] = ent.start_char
            ent._.data['end'] = ent.end_char
            entities.append(ent)

        doc.ents = entities
        return doc
