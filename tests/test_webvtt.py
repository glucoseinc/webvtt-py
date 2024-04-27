import os
import io
import textwrap
from shutil import rmtree, copy

import webvtt
from webvtt.structures import Caption, Style
from .generic import GenericParserTestCase
from webvtt.errors import MalformedFileError


BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')


class WebVTTTestCase(GenericParserTestCase):

    def setUp(self):
        os.makedirs(OUTPUT_DIR)

    def tearDown(self):
        rmtree(OUTPUT_DIR)

    def test_create_caption(self):
        caption = Caption(start='00:00:00.500',
                          end='00:00:07.900',
                          text=['Caption test line 1', 'Caption test line 2']
                          )
        self.assertEqual(caption.start, '00:00:00.500')
        self.assertEqual(caption.start_in_seconds, 0)
        self.assertEqual(caption.end, '00:00:07.900')
        self.assertEqual(caption.end_in_seconds, 7)
        self.assertEqual(caption.lines, ['Caption test line 1', 'Caption test line 2'])

    def test_create_caption_with_text(self):
        caption = Caption(start='00:00:00.500',
                          end='00:00:07.900',
                          text='Caption test line 1\nCaption test line 2'
                          )
        self.assertEqual(caption.start, '00:00:00.500')
        self.assertEqual(caption.start_in_seconds, 0)
        self.assertEqual(caption.end, '00:00:07.900')
        self.assertEqual(caption.end_in_seconds, 7)
        self.assertEqual(caption.lines, ['Caption test line 1', 'Caption test line 2'])

    def test_write_captions(self):
        copy(self._get_file('one_caption.vtt'), OUTPUT_DIR)

        out = io.StringIO()
        vtt = webvtt.read(os.path.join(OUTPUT_DIR, 'one_caption.vtt'))
        new_caption = Caption(start='00:00:07.000',
                              end='00:00:11.890',
                              text=['New caption text line1', 'New caption text line2']
                              )
        vtt.captions.append(new_caption)
        vtt.write(out)

        out.seek(0)

        self.assertListEqual([line for line in out],
                             [
                                 'WEBVTT\n',
                                 '\n',
                                 '00:00:00.500 --> 00:00:07.000\n',
                                 'Caption text #1\n',
                                 '\n',
                                 '00:00:07.000 --> 00:00:11.890\n',
                                 'New caption text line1\n',
                                 'New caption text line2'
                             ]
                             )

    def test_save_captions(self):
        copy(self._get_file('one_caption.vtt'), OUTPUT_DIR)

        vtt = webvtt.read(os.path.join(OUTPUT_DIR, 'one_caption.vtt'))
        new_caption = Caption(start='00:00:07.000',
                              end='00:00:11.890',
                              text=['New caption text line1', 'New caption text line2']
                              )
        vtt.captions.append(new_caption)
        vtt.save()

        with open(os.path.join(OUTPUT_DIR, 'one_caption.vtt'), 'r', encoding='utf-8') as f:
            self.assertListEqual([line for line in f],
                                 [
                                     'WEBVTT\n',
                                     '\n',
                                     '00:00:00.500 --> 00:00:07.000\n',
                                     'Caption text #1\n',
                                     '\n',
                                     '00:00:07.000 --> 00:00:11.890\n',
                                     'New caption text line1\n',
                                     'New caption text line2'
                                 ]
                                 )

    def test_srt_conversion(self):
        copy(self._get_file('one_caption.srt'), OUTPUT_DIR)

        vtt = webvtt.from_srt(os.path.join(OUTPUT_DIR, 'one_caption.srt'))
        vtt.save()

        self.assertTrue(os.path.exists(os.path.join(OUTPUT_DIR, 'one_caption.vtt')))

        with open(os.path.join(OUTPUT_DIR, 'one_caption.vtt'), 'r', encoding='utf-8') as f:
            self.assertListEqual([line for line in f],
                                 [
                                     'WEBVTT\n',
                                     '\n',
                                     '00:00:00.500 --> 00:00:07.000\n',
                                     'Caption text #1',
                                 ]
                                 )

    def test_sbv_conversion(self):
        copy(self._get_file('two_captions.sbv'), OUTPUT_DIR)

        vtt = webvtt.from_sbv(os.path.join(OUTPUT_DIR, 'two_captions.sbv'))
        vtt.save()

        self.assertTrue(os.path.exists(os.path.join(OUTPUT_DIR, 'two_captions.vtt')))

        with open(os.path.join(OUTPUT_DIR, 'two_captions.vtt'), 'r', encoding='utf-8') as f:
            self.assertListEqual([line for line in f],
                                 [
                                     'WEBVTT\n',
                                     '\n',
                                     '00:00:00.378 --> 00:00:11.378\n',
                                     'Caption text #1\n',
                                     '\n',
                                     '00:00:11.378 --> 00:00:12.305\n',
                                     'Caption text #2 (line 1)\n',
                                     'Caption text #2 (line 2)',
                                 ]
                                 )

    def test_save_to_other_location(self):
        target_path = os.path.join(OUTPUT_DIR, 'test_folder')
        os.makedirs(target_path)

        webvtt.read(self._get_file('one_caption.vtt')).save(target_path)
        self.assertTrue(os.path.exists(os.path.join(target_path, 'one_caption.vtt')))

    def test_save_specific_filename(self):
        target_path = os.path.join(OUTPUT_DIR, 'test_folder')
        os.makedirs(target_path)
        output_file = os.path.join(target_path, 'custom_name.vtt')

        webvtt.read(self._get_file('one_caption.vtt')).save(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_save_specific_filename_no_extension(self):
        target_path = os.path.join(OUTPUT_DIR, 'test_folder')
        os.makedirs(target_path)
        output_file = os.path.join(target_path, 'custom_name')

        webvtt.read(self._get_file('one_caption.vtt')).save(output_file)
        self.assertTrue(os.path.exists(os.path.join(target_path, 'custom_name.vtt')))

    def test_caption_timestamp_update(self):
        c = Caption('00:00:00.500', '00:00:07.000')
        c.start = '00:00:01.750'
        c.end = '00:00:08.250'

        self.assertEqual(c.start, '00:00:01.750')
        self.assertEqual(c.end, '00:00:08.250')

    def test_caption_timestamp_format(self):
        c = Caption('01:02:03.400', '02:03:04.500')
        self.assertEqual(c.start, '01:02:03.400')
        self.assertEqual(c.end, '02:03:04.500')

        c = Caption('02:03.400', '03:04.500')
        self.assertEqual(c.start, '00:02:03.400')
        self.assertEqual(c.end, '00:03:04.500')

    def test_caption_text(self):
        c = Caption(text=['Caption line #1', 'Caption line #2'])
        self.assertEqual(
            c.text,
            'Caption line #1\nCaption line #2'
        )

    def test_caption_receive_text(self):
        c = Caption(text='Caption line #1\nCaption line #2')

        self.assertEqual(
            len(c.lines),
            2
        )
        self.assertEqual(
            c.text,
            'Caption line #1\nCaption line #2'
        )

    def test_update_text(self):
        c = Caption(text='Caption line #1')
        c.text = 'Caption line #1 updated'
        self.assertEqual(
            c.text,
            'Caption line #1 updated'
        )

    def test_update_text_multiline(self):
        c = Caption(text='Caption line #1')
        c.text = 'Caption line #1\nCaption line #2'

        self.assertEqual(
            len(c.lines),
            2
        )

        self.assertEqual(
            c.text,
            'Caption line #1\nCaption line #2'
        )

    def test_update_text_wrong_type(self):
        c = Caption(text='Caption line #1')

        self.assertRaises(
            AttributeError,
            setattr,
            c,
            'text',
            123
        )

    def test_manipulate_lines(self):
        c = Caption(text=['Caption line #1', 'Caption line #2'])
        c.lines[0] = 'Caption line #1 updated'
        self.assertEqual(
            c.lines[0],
            'Caption line #1 updated'
        )

    def test_read_file_buffer(self):
        with open(self._get_file('sample.vtt'), 'r', encoding='utf-8') as f:
            vtt = webvtt.from_buffer(f)
            self.assertIsInstance(vtt.captions, list)

    def test_read_memory_buffer(self):
        with open(self._get_file('sample.vtt'), 'r', encoding='utf-8') as f:
            payload = f.read()

        buffer = io.StringIO(payload)
        vtt = webvtt.from_buffer(buffer)
        self.assertIsInstance(vtt.captions, list)

    def test_read_memory_buffer_carriage_return(self):
        """https://github.com/glut23/webvtt-py/issues/29"""
        buffer = io.StringIO(textwrap.dedent('''\
            WEBVTT\r
            \r
            00:00:00.500 --> 00:00:07.000\r
            Caption text #1\r
            \r
            00:00:07.000 --> 00:00:11.890\r
            Caption text #2\r
            \r
            00:00:11.890 --> 00:00:16.320\r
            Caption text #3\r
        '''))
        vtt = webvtt.from_buffer(buffer)
        self.assertEqual(len(vtt.captions), 3)

    def test_read_malformed_buffer(self):
        malformed_payloads = ['', 'MOCK MALFORMED CONTENT']
        for payload in malformed_payloads:
            buffer = io.StringIO(payload)
            with self.assertRaises(MalformedFileError):
                webvtt.from_buffer(buffer)

    def test_captions(self):
        vtt = webvtt.read(self._get_file('sample.vtt'))
        self.assertIsInstance(vtt.captions, list)

    def test_sequence_iteration(self):
        vtt = webvtt.read(self._get_file('sample.vtt'))
        self.assertIsInstance(vtt[0], Caption)
        self.assertEqual(len(vtt), len(vtt.captions))

    def test_save_no_filename(self):
        vtt = webvtt.WebVTT()
        self.assertRaises(
            webvtt.errors.MissingFilenameError,
            vtt.save
        )

    def test_malformed_start_timestamp(self):
        self.assertRaises(
            webvtt.errors.MalformedCaptionError,
            Caption,
            '01:00'
        )

    def test_set_styles_from_text(self):
        style = Style('::cue(b) {\n  color: peachpuff;\n}')
        self.assertListEqual(
            style.lines,
            ['::cue(b) {', '  color: peachpuff;', '}']
        )

    def test_get_styles_as_text(self):
        style = Style(['::cue(b) {', '  color: peachpuff;', '}'])
        self.assertEqual(
            style.text,
            '::cue(b) {\n  color: peachpuff;\n}'
        )

    def test_save_identifiers(self):
        copy(self._get_file('using_identifiers.vtt'), OUTPUT_DIR)

        vtt = webvtt.read(os.path.join(OUTPUT_DIR, 'using_identifiers.vtt'))
        vtt.save(os.path.join(OUTPUT_DIR, 'new_using_identifiers.vtt'))

        with open(os.path.join(OUTPUT_DIR, 'new_using_identifiers.vtt'), 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            'WEBVTT',
            '',
            '00:00:00.500 --> 00:00:07.000',
            'Caption text #1',
            '',
            'second caption',
            '00:00:07.000 --> 00:00:11.890',
            'Caption text #2',
            '',
            '00:00:11.890 --> 00:00:16.320',
            'Caption text #3',
            '',
            '4',
            '00:00:16.320 --> 00:00:21.580',
            'Caption text #4',
            '',
            '00:00:21.580 --> 00:00:23.880',
            'Caption text #5',
            '',
            '00:00:23.880 --> 00:00:27.280',
            'Caption text #6'
        ]

        self.assertListEqual(lines, expected_lines)

    def test_save_updated_identifiers(self):
        copy(self._get_file('using_identifiers.vtt'), OUTPUT_DIR)

        vtt = webvtt.read(os.path.join(OUTPUT_DIR, 'using_identifiers.vtt'))
        vtt.captions[0].identifier = 'first caption'
        vtt.captions[1].identifier = None
        vtt.captions[3].identifier = '44'
        last_caption = Caption('00:00:27.280', '00:00:29.200', 'Caption text #7')
        last_caption.identifier = 'last caption'
        vtt.captions.append(last_caption)
        vtt.save(os.path.join(OUTPUT_DIR, 'new_using_identifiers.vtt'))

        with open(os.path.join(OUTPUT_DIR, 'new_using_identifiers.vtt'), 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            'WEBVTT',
            '',
            'first caption',
            '00:00:00.500 --> 00:00:07.000',
            'Caption text #1',
            '',
            '00:00:07.000 --> 00:00:11.890',
            'Caption text #2',
            '',
            '00:00:11.890 --> 00:00:16.320',
            'Caption text #3',
            '',
            '44',
            '00:00:16.320 --> 00:00:21.580',
            'Caption text #4',
            '',
            '00:00:21.580 --> 00:00:23.880',
            'Caption text #5',
            '',
            '00:00:23.880 --> 00:00:27.280',
            'Caption text #6',
            '',
            'last caption',
            '00:00:27.280 --> 00:00:29.200',
            'Caption text #7'
        ]

        self.assertListEqual(lines, expected_lines)

    def test_content_formatting(self):
        """
        Verify that content property returns the correctly formatted webvtt.
        """
        captions = [
            Caption('00:00:00.500', '00:00:07.000', ['Caption test line 1', 'Caption test line 2']),
            Caption('00:00:08.000', '00:00:15.000', ['Caption test line 3', 'Caption test line 4']),
        ]
        expected_content = textwrap.dedent("""
            WEBVTT

            00:00:00.500 --> 00:00:07.000
            Caption test line 1
            Caption test line 2

            00:00:08.000 --> 00:00:15.000
            Caption test line 3
            Caption test line 4
            """).strip()
        vtt = webvtt.WebVTT(captions=captions)
        self.assertEqual(expected_content, vtt.content)
