from diploma import *
from unittest.mock import patch
import unittest
import json


class TestVkinder(unittest.TestCase):

    def test_params(self):
        with patch('diploma.input', side_effect=["sex", "2"]):
            func_result1 = user1.get_partners()
            list1 = len(func_result1)
        with patch('diploma.input', side_effect=["age_from", "25"]):
            func_result2 = user1.get_partners()
            list2 = len(func_result2)
        with patch('diploma.input', side_effect=["age_to", "35"]):
            func_result3 = user1.get_partners()
            list3 = len(func_result3)
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            func_result4 = user1.get_partners()
            list4 = len(func_result4)
        with patch('diploma.input', side_effect=["religion", "православие"]):
            func_result5 = user1.get_partners()
            list5 = len(func_result5)
        with patch('diploma.input', side_effect=["position", "менеджер"]):
            func_result6 = user1.get_partners()
            list6 = len(func_result6)
        with patch('diploma.input', side_effect=["sex, age_from, age_to, hometown, religion, position, interests",
                                                 "2", "25", "35", "Москва", "православие", "менеджер", "путешествия"]):
            func_result7 = user1.get_partners()
            list7 = len(func_result7)
        self.assertEqual(list1, list2, list3)
        self.assertEqual(list3, list4, list5)
        self.assertEqual(list5, list6, list7)

    def test_uniqueness(self):
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            user1.get_partners()
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            user1.get_partners()
            with open('previous-results.txt') as f:
                length1 = len(f.read())
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            user1.get_partners()
            with open('previous-results.txt') as f:
                length2 = len(f.read())
        self.assertLess(length1, length2)

        with open('previous-results.txt', 'w') as f:
            f.write('')
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            final_list = user1.get_partners()
            with open('previous-results.txt') as f:
                previous_results = f.read()
                for person in final_list:
                    self.assertIn(str(person['id']), previous_results)

        with open('previous-results.txt', 'w') as f:
            f.write('')
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            user1.get_partners()
            with open('previous-results.txt') as f:
                res1 = f.read()
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            user1.get_partners()
            with open('previous-results.txt') as f:
                res2 = f.read()
        self.assertNotEqual(res1+res1, res2)

    def test_json(self):
        with patch('diploma.input', side_effect=["hometown", "Москва"]):
            res = user1.add_top3_photos_json()
            with open('vkinder.json') as file:
                json_file = json.load(file)
            for person in res:
                self.assertIn(person, json_file)


if __name__ == '__main__':
    unittest.main()
