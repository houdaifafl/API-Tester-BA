from fpdf import FPDF
from fpdf.enums import XPos, YPos

TITLE_COLOR   = (30, 30, 30)
HEADING_COLOR = (30, 100, 180)
CODE_BG       = (245, 245, 245)
CODE_COLOR    = (40, 40, 40)
BODY_COLOR    = (50, 50, 50)
SUBTLE        = (120, 120, 120)

class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*SUBTLE)
        self.cell(0, 8, 'APICraft -- Comprehensive Features & Diversity Analysis', align='L',
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

    def list_item(self, title, text):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*HEADING_COLOR)
        self.cell(4, 6, '-', align='L')
        self.cell(self.get_string_width(title) + 1, 6, title)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*BODY_COLOR)
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def table(self, headers, rows):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(*HEADING_COLOR)
        self.set_text_color(255, 255, 255)
        
        total_width = self.w - self.l_margin - self.r_margin
        col_w1 = total_width * 0.30
        col_w2 = total_width * 0.45
        col_w3 = total_width * 0.25
        
        self.cell(col_w1, 7, headers[0], border=1, fill=True)
        self.cell(col_w2, 7, headers[1], border=1, fill=True)
        self.cell(col_w3, 7, headers[2], border=1, fill=True)
        self.ln()
        
        self.set_font('Helvetica', '', 9)
        fill = False
        for row in rows:
            self.set_fill_color(235, 243, 255) if fill else self.set_fill_color(255, 255, 255)
            self.set_text_color(*BODY_COLOR)
            self.cell(col_w1, 7, row[0], border=1, fill=True)
            self.cell(col_w2, 7, row[1], border=1, fill=True)
            self.cell(col_w3, 7, row[2], border=1, fill=True)
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
    pdf.multi_cell(0, 12, 'APICraft Architecture Analysis', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(*HEADING_COLOR)
    pdf.multi_cell(0, 8, 'A Comprehensive Evaluation of Feature Diversity\nand Architectural Paradigms',
                   align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_draw_color(*HEADING_COLOR)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(6)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*SUBTLE)
    pdf.cell(0, 6, 'Subject: Fullstack Codebase Diversity Evaluation', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Project: APICraft API Testing Suite', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Author: AI Agent Peer Review', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # ── 1. Executive Summary ──────────────────────────────────────────────────
    pdf.section_title('1. Executive Summary')
    pdf.body(
        'This report presents a thorough analysis of the features implemented in the APICraft project '
        'to evaluate whether there is a broad, qualitative diversity in the "art" (i.e. engineering '
        'disciplines, algorithms, design patterns, and programming models) of the features. '
        'The findings demonstrate that APICraft goes far beyond standard CRUD (Create, Read, Update, Delete) '
        'systems, integrating complex elements of security, systems proxying, visual analytics, '
        'transaction boundaries, and AST analysis.'
    )

    # ── 2. Detailed Features Inventory ─────────────────────────────────────────
    pdf.section_title('2. Core Features Inventory')
    pdf.body(
        'The codebase consists of several highly specialized modules that target distinct operational requirements:'
    )
    pdf.ln(1)
    pdf.list_item('Secure HTTP Proxy Gateway: ', 'Executes network requests with customizable query parameters, headers, authentication context, and request bodies. Implements validation loops to block SSRF (Server-Side Request Forgery) attacks and resolve local/private IP ranges dynamically.')
    pdf.list_item('Identity & Access Control: ', 'Protects resources using a token-based JWT (HMAC-SHA256) signature and password hashing via bcrypt. Controls resource modifications by validating workspace roles (Admin, Member, Viewer).')
    pdf.list_item('Chronological Audit Logging: ', 'Hooks workspace collections and request updates to log chronological actions, diffing the before and after states using structured JSON columns.')
    pdf.list_item('Comments & Key-Cascading Annotations: ', 'Allows users to pin comments to specific requests, tabs, or input variables. Automates name cascading so that renaming a request parameter shifts comment target keys automatically.')
    pdf.list_item('Analytics Dashboard: ', 'Compiles request stats over the history database, showing rolling percentile response times, failure rates, and activity volume using recharts.')
    pdf.list_item('Request Exporters: ', 'Serializes client state into terminal-runnable bash cURL strings and downloads formatted JSON request templates.')

    # ── 3. Diversity in the "Art" ──────────────────────────────────────────────
    pdf.section_title('3. Analysis of Structural Diversity')
    pdf.body(
        'Diversity in the "art" of software engineering implies applying multiple paradigms '
        'and handling distinct constraints. APICraft displays substantial diversity across:'
    )
    pdf.ln(1)
    pdf.sub_title('Systems Programming vs. Application Workflows')
    pdf.body(
        'The codebase bridges standard workflow orchestrations (like sending workspace invitations '
        'and accepting pending requests) with low-level systems proxying (like analyzing IP addresses, '
        'controlling redirect counts, and filtering loopback socket connections).'
    )
    pdf.ln(2)
    pdf.sub_title('Deterministic Transactions vs. Asynchronous Visualizers')
    pdf.body(
        'The application handles transactional data constraints in the database layer (cascade '
        'rules, nullable constraints, and triggers) while concurrently rendering highly '
        'interactive, asynchronous UI modules (like charts and sliding log grids) on the React frontend.'
    )

    # ── 4. Paradigm Mapping ──────────────────────────────────────────────────
    pdf.section_title('4. Programming Paradigms Mapping')
    pdf.table(
        ['Feature Area', 'Paradigms & Algorithms', 'Engineering Area'],
        [
            ['API proxy execute', 'SSRF Validation, Socket parsing, Redirect guards', 'System & Network Security'],
            ['Token authorization', 'HMAC-SHA256 cryptography, JWT decoder, btoa', 'Web Cryptography'],
            ['Cascading database updates', 'Cascade deletion constraints, synchronization triggers', 'Relational Database Design'],
            ['Audit logs & Diffs', 'Structured JSON diffing, rolling audit trail grids', 'Audit Compliance & Systems Log'],
            ['Analytics Charts', 'SQL Aggregations, Recharts, data normalization', 'Data Engineering & Analytics'],
            ['cURL Export utilities', 'Bash string parsing, escaping, Blob downloads', 'Serialization Utilities'],
            ['API Drift Verification', 'AST route parsing, Schema validation, pytest', 'Quality Assurance & Testing'],
        ]
    )

    # ── 5. Conclusion ────────────────────────────────────────────────────────
    pdf.section_title('5. Conclusion')
    pdf.body(
        'APICraft displays a high degree of architectural diversity. It requires a developer to master '
        'multiple distinct disciplines - spanning database schema design, web security, cryptographic '
        'token validation, frontend state caching, and automation testing. This variety demonstrates '
        'a rich and mature software development cycle, representing an excellent showcase of '
        'advanced computer engineering principles.'
    )

    out = r'c:\Users\hlanj\Bachelor info\Bachelor Arbeit\API tester\APICraft_Features_Diversity_Analysis_Report.pdf'
    pdf.output(out)
    print(f'PDF saved to: {out}')

if __name__ == '__main__':
    build()
