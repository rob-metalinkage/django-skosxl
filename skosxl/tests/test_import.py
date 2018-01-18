from skosxl.models import *
from django.core.files.uploadedfile import SimpleUploadedFile



from django.test import TestCase

PREFIX = """@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix test: <http://example.org/> .
"""

SCHEME1 = """
test:scheme1 a skos:ConceptScheme ;
    rdfs:label "Test concept scheme"@en.
"""

SCHEME2 = """
test:scheme2 a skos:ConceptScheme .
"""

CONCEPT1 = """
test:Concept_defaultlang a skos:Concept ;
    skos:prefLabel "A label in default language" ;
    skos:inScheme test:scheme1 ;
    .

"""

CONCEPT_S2 = """
test:ConceptS2_1 a skos:Concept ;
    skos:prefLabel "A concept in another scheme" ;
    skos:inScheme test:scheme2 ;
    .

"""

CONCEPT2 = """
test:Concept_specificlang a skos:Concept ;
    skos:prefLabel "Incroyable"@fr ;
    skos:inScheme test:scheme1 ;
    .

"""
SUITE_TEST = "".join(( PREFIX, SCHEME1, CONCEPT1, CONCEPT2))

class SchemeImportTestCase(TestCase):
    """ Test case for importing a concept scheme """
    
    def setUp(self):
        pass
        
    def test_scheme_in_file(self):
        loadtest = ImportedConceptScheme(id=1, resource_type=ImportedConceptScheme.TYPE_INSTANCE, force_bulk_only=False, force_refresh=True)
        loadtest.file = SimpleUploadedFile('test.ttl', "".join( (PREFIX,SCHEME1,CONCEPT1) ))
        loadtest.save()
        cs = Scheme.objects.get(uri="http://example.org/scheme1")
        concepts= list(cs.concept_set.all())
        self.assertEqual(cs.uri,"http://example.org/scheme1")
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0].pref_label, u'A label in default language')

    def test_scheme_set(self):
        """ tests scheme defined by metadata, file only has concepts """
        loadtest = ImportedConceptScheme(id=1, resource_type=ImportedConceptScheme.TYPE_INSTANCE, force_bulk_only=False, force_refresh=True)
        loadtest.target_scheme = 'http://example.org/scheme1'
        loadtest.file = SimpleUploadedFile('test.ttl', "".join( (PREFIX,CONCEPT1) ))
        loadtest.save()
        cs = Scheme.objects.get(uri="http://example.org/scheme1")
        concepts= list(cs.concept_set.all())
        self.assertEqual(cs.uri,"http://example.org/scheme1")
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0].pref_label, u'A label in default language')

    def test_scheme_multiple(self):
        """ test loads concept from one of multiple schemes declared in file """
        loadtest = ImportedConceptScheme(id=1, resource_type=ImportedConceptScheme.TYPE_INSTANCE, force_bulk_only=False, force_refresh=True)
        loadtest.target_scheme = 'http://example.org/scheme1'
        loadtest.file = SimpleUploadedFile('test.ttl', "".join( (PREFIX,SCHEME1, SCHEME2, CONCEPT1, CONCEPT_S2) ))
        loadtest.save()
        cs = Scheme.objects.get(uri="http://example.org/scheme1")
        concepts= list(cs.concept_set.all())
       
        self.assertEqual(cs.uri,"http://example.org/scheme1")
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0].pref_label, u'A label in default language')
        
class ConceptDetailsTestCase(TestCase):
    """ Loads a complete set of features, then tests each individual one """
    def setUp(self):
        loadtest = ImportedConceptScheme(id=1, resource_type=ImportedConceptScheme.TYPE_INSTANCE, force_bulk_only=False, force_refresh=True)
        loadtest.file = SimpleUploadedFile('test.ttl', SUITE_TEST)
        loadtest.save() 

    def test_preflabel_defaultlang(self):
        """ tests a pref label is set using the default language if lang not specified """
        l = Label.objects.get(concept__term="Concept_defaultlang", label_text="A label in default language")
        self.assertEqual(l.language, DEFAULT_LANG)

    def test_preflabel_specificlang(self):
        """ tests a pref label is set using the default language if lang not specified """
        l = Label.objects.get(concept__term="Concept_specificlang", language="fr")
        self.assertEqual(l.language, "fr")
        
#    def test_metaprops(self):        