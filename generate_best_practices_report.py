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
        self.cell(0, 8, 'Best Practices for AI-Agent Collaborations', align='L',
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

    def list_item(self, bullet, text):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*HEADING_COLOR)
        self.cell(6, 6, bullet, align='L')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*BODY_COLOR)
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def table(self, headers, rows):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(*HEADING_COLOR)
        self.set_text_color(255, 255, 255)
        
        # Calculate column widths to fit margins perfectly
        total_width = self.w - self.l_margin - self.r_margin
        col_w1 = total_width * 0.25
        col_w2 = total_width * 0.55
        col_w3 = total_width * 0.20
        
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
            
            # Use multi_cell or simple cell depending on line length
            x_before = self.get_x()
            y_before = self.get_y()
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
    pdf.multi_cell(0, 12, 'Best Practices Report', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(*HEADING_COLOR)
    pdf.multi_cell(0, 8, 'Guidelines for Effective Collaboration\nwith AI Coding Agents in Complex Software Projects',
                   align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_draw_color(*HEADING_COLOR)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(6)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*SUBTLE)
    pdf.cell(0, 6, 'Subject: Developer & AI Agent Pair Programming', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Context: APICraft API Testing Full-stack Application', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, 'Date: July 2026', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # ── 1. Introduction ──────────────────────────────────────────────────────
    pdf.section_title('1. Executive Summary')
    pdf.body(
        'Agentic AI software engineers are highly capable of navigating multi-file codebases, '
        'refactoring features, and automating test procedures. However, without strict '
        'governance, AI agents can suffer from context drift, make poor architectural assumptions, '
        'and degrade codebase quality. This report compiles the key collaboration best '
        'practices derived from our development sessions on the APICraft project.'
    )

    # ── 2. Design-First Workflow ──────────────────────────────────────────────
    pdf.section_title('2. The Two-Phase Workflow (Design Before Code)')
    pdf.body(
        'The absolute most critical best practice is enforcing a strict boundary between '
        'the design phase and the execution phase. An agent must not be permitted to write '
        'implementation code until the human developer has approved the blueprint.'
    )
    pdf.ln(1)
    pdf.list_item('- ', 'Phase 1: Design & Alignment: Request the agent to produce a structured "implementation_plan.md". This plan must outline the architectural rationale, file changes, data flow, state management, and potential side-effects before any source code is changed.')
    pdf.list_item('- ', 'Phase 2: Review Gate: The human acts as a gatekeeper. If the plan lacks specificity, reuse of components, or contains bad design patterns, the plan must be rejected. The agent only proceeds upon receiving explicit approval.')

    # ── 3. Logic & Presentation Separation ────────────────────────────────────
    pdf.section_title('3. Architectural Separation (SRP & Utility Isolation)')
    pdf.body(
        'Keep React components and backend routes focused strictly on presentation and thin coordination. '
        'Complex logic must be isolated to make it easier for both agents and humans to debug and maintain.'
    )
    pdf.ln(1)
    pdf.list_item('- ', 'Isolate Complexity: Extract data transformation, formatting, and file serialization code (such as generateCurlCommand) into pure, vanilla JavaScript/Python modules (e.g., requestExportUtils.js).')
    pdf.list_item('- ', 'Improve Testability: Pure utilities have no dependencies on frameworks, React hooks, or context states, making them 100% testable via isolated unit test scripts.')
    pdf.list_item('- ', 'Adhere to Component Limits: Enforce a strict line-limit (e.g., ~150 lines of JSX) for UI files. If a component grows beyond this, require the agent to extract logic into helpers or custom hooks.')

    # ── 4. Project Rules & Constraints ────────────────────────────────────────
    pdf.section_title('4. Codebase Governance (AGENTS.md Rules)')
    pdf.body(
        'Grounding the agent in explicit project instructions prevents style drift, '
        'improper library imports, and architectural degradation.'
    )
    pdf.ln(1)
    pdf.list_item('- ', 'Ground Rules File: Create a permanent AGENTS.md or CLAUDE.md in the workspace customization root containing codebase conventions, style guidelines, and forbidden patterns.')
    pdf.list_item('- ', 'State Model Compliance: Enforce a strict state model (e.g., global auth context, feature-level hooks, and local UI state) to prevent redundant states or prop-drilling.')
    pdf.list_item('- ', 'Track Structure Maps: Maintain a living FRONTEND_STRUCTURE.md and BACKEND_STRUCTURE.md, and require the agent to update them as files are added or modified, keeping codebase maps fresh.')

    # ── 5. Multi-Tier Verification ────────────────────────────────────────────
    pdf.section_title('5. Multi-Tier Verification Loops')
    pdf.body(
        'Testing must be requirement-driven and verified across multiple levels to catch all potential bugs.'
    )
    pdf.ln(1)
    pdf.list_item('- ', 'Tier 1: Backend Integration Tests: Execute real API calls against test databases using frameworks like pytest. Ensure endpoints are documented in openapi.yaml and verify drift.')
    pdf.list_item('- ', 'Tier 2: Component Smoke Tests: Confirm components render without crashing. Test the pure helper utilities with Jest unit tests covering edge cases (such as single-quote escaping).')
    pdf.list_item('- ', 'Tier 3: Browser E2E Verification: For UI features, use a browser agent to log in, interact with the app, record a demo, and capture screenshots. This catches CSS rendering bugs and routing failures.')

    # ── 6. Verification Table ────────────────────────────────────────────────
    pdf.section_title('6. Summary Checklist for AI Agent Tasks')
    pdf.table(
        ['Collaboration Stage', 'Deliverable / Action Required', 'Responsible Entity'],
        [
            ['1. Clarification', 'Map options, discuss import/export scopes, align on UX', 'Developer & Agent'],
            ['2. Planning', 'Generate implementation_plan.md detailing all files', 'Agent (Architect)'],
            ['3. Approval Gate', 'Review Design Review and type explicit approval', 'Developer'],
            ['4. Coding', 'Implement features sequentially following dependency order', 'Agent (Implementer)'],
            ['5. Testing', 'Run pytest (backend) and Jest (frontend utils/smoke)', 'Agent & Test Runner'],
            ['6. E2E Verification', 'Start full stack, verify UI flow, output demo and logs', 'Agent (Browser)'],
            ['7. Review Report', 'Generate review_report.md auditing SRP and coupling', 'Agent (Reviewer)'],
        ]
    )

    pdf.body(
        'Following these checklists keeps development cycles clean, eliminates regressions, '
        'and ensures that the developer stays in full control of the codebase architecture.'
    )

    out = r'c:\Users\hlanj\Bachelor info\Bachelor Arbeit\API tester\Best_Practices_AI_Agent_Collaborations.pdf'
    pdf.output(out)
    print(f'PDF saved to: {out}')

if __name__ == '__main__':
    build()
