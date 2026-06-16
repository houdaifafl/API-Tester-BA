from fpdf import FPDF
from fpdf.enums import XPos, YPos

TITLE_COLOR   = (30, 30, 30)
HEADING_COLOR = (30, 100, 180)
CODE_BG       = (245, 245, 245)
CODE_COLOR    = (40, 40, 40)
BODY_COLOR    = (50, 50, 50)
RED           = (180, 30, 30)
GREEN         = (30, 140, 60)
SUBTLE        = (120, 120, 120)


class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*SUBTLE)
        self.cell(0, 8, 'Failure Report -- Signup Bypasses create_workspace', align='L',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*SUBTLE)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*SUBTLE)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def section_title(self, text):
        self.ln(4)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(*HEADING_COLOR)
        self.cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*HEADING_COLOR)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_text_color(*BODY_COLOR)

    def sub_title(self, text):
        self.ln(2)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*TITLE_COLOR)
        self.multi_cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BODY_COLOR)

    def body(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*BODY_COLOR)
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def label(self, text, color=None):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*(color or BODY_COLOR))
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BODY_COLOR)

    def code_block(self, lines):
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(200, 200, 200)
        x = self.l_margin
        y = self.get_y() + 1
        line_h = 5.5
        padding = 4
        block_h = len(lines) * line_h + padding * 2
        self.rect(x, y, self.w - self.l_margin - self.r_margin, block_h, 'FD')
        self.set_xy(x + padding, y + padding)
        self.set_font('Courier', '', 8.5)
        self.set_text_color(*CODE_COLOR)
        for line in lines:
            self.set_x(x + padding)
            self.cell(0, line_h, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(padding + 1)
        self.set_text_color(*BODY_COLOR)

    def inline_badge(self, text, color):
        self.set_font('Courier', 'B', 9)
        self.set_text_color(*color)
        self.cell(self.get_string_width(text) + 2, 6, text)
        self.set_text_color(*BODY_COLOR)
        self.set_font('Helvetica', '', 10)

    def table(self, headers, rows):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(*HEADING_COLOR)
        self.set_text_color(255, 255, 255)
        col_w = (self.w - self.l_margin - self.r_margin) / len(headers)
        for h in headers:
            self.cell(col_w, 7, h, border=1, fill=True)
        self.ln()
        self.set_font('Helvetica', '', 9)
        fill = False
        for row in rows:
            self.set_fill_color(235, 243, 255) if fill else self.set_fill_color(255, 255, 255)
            self.set_text_color(*BODY_COLOR)
            for cell in row:
                self.cell(col_w, 7, cell, border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(3)


def build():
    pdf = PDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Cover ────────────────────────────────────────────────────────────────
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(*TITLE_COLOR)
    pdf.multi_cell(0, 12, 'Failure Report', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(*HEADING_COLOR)
    pdf.multi_cell(0, 8, 'Signup Bypasses create_workspace\nBreaking Collection Tests',
                   align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_draw_color(*HEADING_COLOR)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(6)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*SUBTLE)
    pdf.cell(0, 6, 'Project: APICraft -- API Tester', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Test file: backend/tests/test_collections.py', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Date: 2026-06-16', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # ── 1. The Symptom ───────────────────────────────────────────────────────
    pdf.section_title('1. The Symptom')
    pdf.body('Two tests failed on the first run of test_collections.py:')

    pdf.code_block([
        'FAILED tests/test_collections.py::TestListCollections::test_returns_all_collections',
        'FAILED tests/test_collections.py::TestDeleteCollection::test_deleted_collection_not_in_list',
    ])

    pdf.sub_title('Failure 1 output')
    pdf.code_block([
        'assert len(cols) == 3',
        'AssertionError: assert 2 == 3',
    ])

    pdf.sub_title('Failure 2 output')
    pdf.code_block([
        'assert col_id not in col_ids',
        'AssertionError: assert 1 not in [1]',
    ])

    pdf.body(
        'Both tests operated on the default workspace created during signup and expected '
        'a default collection to already exist inside it. Neither had ever called the '
        'collections list endpoint before performing write operations.'
    )

    # ── 2. Root Cause ────────────────────────────────────────────────────────
    pdf.section_title('2. Root Cause -- signup_user Creates the Workspace Directly')

    pdf.body(
        'The auth_service.signup_user function creates the default workspace by instantiating '
        'the Workspace model directly and committing it. It never calls '
        'workspace_service.create_workspace, which is the only other path that seeds a default collection.'
    )

    pdf.sub_title('backend/services/auth_service.py')
    pdf.code_block([
        'def signup_user(username, first_name, email, password):',
        '    # ...',
        '    user = User(username=username, first_name=first_name, ...)',
        '    db.session.add(user)',
        '    db.session.flush()',
        '',
        '    # Workspace created directly -- create_workspace() is never called',
        '    default_workspace = Workspace(',
        '        name=f"{first_name}\'s Space", user_id=user.id, is_default=True',
        '    )',
        '    db.session.add(default_workspace)',
        '    db.session.commit()   # no ensure_default_collection() here',
        '    return user, None',
    ])

    pdf.body(
        'Compare this to workspace_service.create_workspace, which seeds the default '
        'collection immediately via ensure_default_collection:'
    )

    pdf.sub_title('backend/services/workspace_service.py')
    pdf.code_block([
        'def create_workspace(user_id, name):',
        '    workspace = Workspace(name=name, user_id=user_id)',
        '    db.session.add(workspace)',
        '    db.session.flush()',
        '    ensure_default_collection(workspace.id)  # <- never reached from signup',
        '    return {\'id\': workspace.id, \'name\': workspace.name, ...}',
    ])

    pdf.body(
        'Because signup_user skips this entirely, the default workspace is created with zero '
        'collections. The default collection ("My Collection") is only seeded lazily -- the first '
        'time GET /api/workspaces/{id}/collections is called:'
    )

    pdf.sub_title('backend/services/collection_service.py')
    pdf.code_block([
        'def get_collections_by_workspace(workspace_id):',
        '    ensure_default_collection(workspace_id)  # <- seeding only happens here',
        '    collections = Collection.query.filter_by(workspace_id=workspace_id).all()',
        '    return [_serialize(c) for c in collections]',
        '',
        'def ensure_default_collection(workspace_id):',
        '    exists = Collection.query.filter_by(workspace_id=workspace_id).first()',
        '    if not exists:',
        '        collection = Collection(',
        '            name=\'My Collection\', workspace_id=workspace_id, is_default=True',
        '        )',
        '        db.session.add(collection)',
        '        db.session.flush()',
        '        db.session.add(Request(name=\'Get data\',  method=\'GET\',  ...))',
        '        db.session.add(Request(name=\'Post data\', method=\'POST\', ...))',
        '        db.session.commit()',
    ])

    # ── 3. Why Each Test Failed ──────────────────────────────────────────────
    pdf.section_title('3. Why Each Test Failed')

    pdf.sub_title('test_returns_all_collections')
    pdf.body(
        'The test assumed the default collection already existed after signup and expected '
        '3 total collections after adding 2 more:'
    )
    pdf.code_block([
        'def test_returns_all_collections(self, client, auth_data):',
        '    ws_id = auth_data[\'default_workspace_id\']',
        '    client.post(f\'/api/workspaces/{ws_id}/collections\')  # ID=1, is_default=False',
        '    client.post(f\'/api/workspaces/{ws_id}/collections\')  # ID=2, is_default=False',
        '    cols = client.get(f\'/api/workspaces/{ws_id}/collections\').get_json()',
        '    assert len(cols) == 3  # FAILS -- only 2 exist, default was never seeded',
    ])
    pdf.body(
        'The final GET calls ensure_default_collection, but since 2 collections already '
        'exist, the guard "if not exists" prevents any new seeding. The result is 2, not 3.'
    )

    pdf.ln(2)
    pdf.sub_title('test_deleted_collection_not_in_list -- compounded by SQLite ID reuse')
    pdf.body(
        'This failure had a second layer. After deleting the only collection from an unseeded '
        'workspace, the table became empty. ensure_default_collection then auto-created a fresh '
        'default collection -- and SQLite\'s INTEGER PRIMARY KEY (without AUTOINCREMENT) reuses '
        'IDs when the table is empty, assigning the new default collection the same ID=1 as '
        'the deleted one.'
    )
    pdf.code_block([
        'def test_deleted_collection_not_in_list(self, client, auth_data):',
        '    ws_id = auth_data[\'default_workspace_id\']',
        '    col_id = self._create_non_default(...)["id"]  # ID=1 (first in empty table)',
        '    client.delete(f\'/api/collections/{col_id}\')   # deletes ID=1',
        '    col_ids = [c["id"] for c in client.get(...).get_json()]',
        '    # ensure_default_collection fires, creates new default -- gets ID=1 again!',
        '    assert col_id not in col_ids  # FAILS: assert 1 not in [1]',
    ])

    # ── 4. How the Agent Diagnosed It ───────────────────────────────────────
    pdf.section_title('4. How the Agent Diagnosed It')

    pdf.body(
        'After seeing both failures trace back to auth_data[\'default_workspace_id\'], '
        'the agent read auth_service.py directly. Tracing the signup flow confirmed that '
        'Workspace is instantiated without ever calling create_workspace or '
        'ensure_default_collection.'
    )
    pdf.body(
        'Cross-referencing workspace_service.create_workspace showed that seeding only '
        'happens through that function. Since signup bypasses it, the workspace is created '
        'empty and the seeding is entirely deferred to the first GET.'
    )
    pdf.body(
        'The SQLite ID reuse was inferred directly from the error output: '
        '"assert 1 not in [1]". A deleted ID reappearing in a fresh insert is only possible '
        'when the table is empty and SQLite reassigns the lowest available integer. This '
        'confirmed the table had been fully emptied before the re-seeding occurred.'
    )

    # ── 5. The Fix ───────────────────────────────────────────────────────────
    pdf.section_title('5. The Fix')

    pdf.body(
        'Both tests were corrected by adding one GET call before any write operations. '
        'This forces ensure_default_collection to run, occupying ID=1 before any '
        'non-default collections are created. All subsequent inserts receive higher IDs '
        'and no collision is possible.'
    )

    pdf.sub_title('test_returns_all_collections -- fixed')
    pdf.code_block([
        'def test_returns_all_collections(self, client, auth_data):',
        '    ws_id = auth_data[\'default_workspace_id\']',
        '    client.get(f\'/api/workspaces/{ws_id}/collections\')  # seeds default (ID=1)',
        '    client.post(f\'/api/workspaces/{ws_id}/collections\') # ID=2',
        '    client.post(f\'/api/workspaces/{ws_id}/collections\') # ID=3',
        '    cols = client.get(f\'/api/workspaces/{ws_id}/collections\').get_json()',
        '    assert len(cols) == 3  # PASSES',
    ])

    pdf.sub_title('test_deleted_collection_not_in_list -- fixed')
    pdf.code_block([
        'def test_deleted_collection_not_in_list(self, client, auth_data):',
        '    ws_id = auth_data[\'default_workspace_id\']',
        '    client.get(f\'/api/workspaces/{ws_id}/collections\')  # seeds default (ID=1)',
        '    col_id = self._create_non_default(...)["id"]  # ID=2',
        '    client.delete(f\'/api/collections/{col_id}\')   # deletes ID=2',
        '    col_ids = [c["id"] for c in client.get(...).get_json()]',
        '    assert col_id not in col_ids  # PASSES: assert 2 not in [1]',
    ])

    # ── 6. Design Inconsistency Exposed ─────────────────────────────────────
    pdf.section_title('6. Design Inconsistency Exposed by the Failure')

    pdf.body(
        'The failure revealed that two workspace creation paths behave differently. '
        'Any code that assumes a workspace always has a collection immediately after '
        'creation (e.g. a background job, import feature, or API consumer) would find '
        'an empty workspace if it was created through signup.'
    )

    pdf.table(
        ['Creation path', 'Seeds default collection?'],
        [
            ['POST /api/workspaces  ->  workspace_service.create_workspace()', 'Yes -- immediately'],
            ['Signup  ->  auth_service.signup_user()', 'No -- only on first GET /collections'],
        ]
    )

    pdf.body(
        'The tests made this implicit assumption visible and permanently documented. '
        'Any future developer reading these tests will see exactly why the GET call '
        'must precede write operations in this context.'
    )

    out = r'c:\Users\hlanj\Bachelor info\Bachelor Arbeit\API tester\failure_report_signup_workspace.pdf'
    pdf.output(out)
    print(f'PDF saved to: {out}')


if __name__ == '__main__':
    build()
