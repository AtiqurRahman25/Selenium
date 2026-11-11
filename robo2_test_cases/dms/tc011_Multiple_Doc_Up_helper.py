"""
Shared helpers for the pending-documents page (Document Type search, meta-data form,
confirmation message). Re-exports common.py utilities for backward compatibility.
"""
import common as c

ATTACH_URL = c.ATTACH_URL
PENDING_URL = c.PENDING_URL
FILE_INPUT = c.FILE_INPUT
DOC_TYPE_BOX = c.DOC_TYPE_BOX
DOC_TYPE_RESULTS = c.DOC_TYPE_RESULTS
DOC_TYPE_SEARCH_BOX = c.DOC_TYPE_SEARCH_BOX
DOC_TYPE_OPTION = c.DOC_TYPE_OPTION
DOC_TYPE_SEARCH_TERMS = c.DOC_TYPE_SEARCH_TERMS
METADATA_PANEL = c.METADATA_PANEL
UPLOAD_BTN = c.UPLOAD_BTN
MESSAGE_BOX = c.MESSAGE_BOX
SUCCESS_WORDS = c.SUCCESS_WORDS
ERROR_WORDS = c.ERROR_WORDS

body_text = c.body_text
pending_row_icon = c.pending_row_icon
clear_selected_files = c.clear_selected_files
select_document_type = c.select_document_type
fill_metadata_form = c.fill_metadata_form
wait_for_message = c.wait_for_message
xpath_text = c.xpath_text
popup_text = c.popup_text
short = c.short
fail = c.fail
selected_count = c.selected_count
