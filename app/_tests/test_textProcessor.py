from unittest import TestCase
from app.text_processor import TextProcessor


class TestTextProcessor(TestCase):

    def setUp(self) -> None:
        self.processor = TextProcessor()

    def test__find_variable_pattern(self):
        test_text = """ This is example text to test against.  There are lists: [ITEM-LIST1]
        In addition to lists, there are variables {product_name} that should be the product name.  There are also figures: [ITEM-FIGURE1]
        and not found figures [ITEM-FIGURE2].
        Finally, lets have a table: [ITEM-TABLE1]
        """

        patterns = self.processor._find_variable_patterns(text=test_text)
        self.assertEqual(len(patterns), 4)
        self.assertListEqual(patterns, ['[ITEM-LIST1]', '[ITEM-FIGURE1]', '[ITEM-FIGURE2]', '[ITEM-TABLE1]'])

    def test__find_variable_pattern_with_Multiple_ITEM_on_line(self):
        test_text = "This should throw an error! [ITEM-FIGURE1] [ITEM-FIGURE2]"

        with self.assertRaises(AssertionError):
            self.processor._find_variable_patterns(text=test_text)

    def test__find_variable_pattern_with_no_ITEMS(self):
        test_text = "There are no items here! Just text!"

        patterns = self.processor._find_variable_patterns(text=test_text)
        self.assertEqual(len(patterns), 0)
        self.assertListEqual(patterns, [])

    def test_processText(self):
        test_text = """ This is example text to test against.  There are lists: [ITEM-LIST1]
                In addition to lists, there are variables {product_name} that should be the product name.  There are also figures: [ITEM-FIGURE1]
                and not found figures [ITEM-FIGURE2]
                Finally, lets have a table: [ITEM-TABLE1]
                """

        for thing in self.processor.process_text(test_text):
            print(thing)
