from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import math

def draw_header(c, width, height, oracle_blue):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(oracle_blue)
    c.drawString(0.75*inch, height - 0.5*inch, "[ORACLE TECHNICAL SPECIFICATION // TS-001]")
    c.setStrokeColor(oracle_blue)
    c.setLineWidth(0.5)
    c.line(0.75*inch, height - 0.6*inch, width - 0.75*inch, height - 0.6*inch)

def draw_footer(c, width, height, slate_grey):
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(slate_grey)
    c.drawCentredString(width/2, 0.4*inch, "© 2026 JMc Associates LLC // James McCabe | ModernCYPH3R.com // Confidential Transmission")

def draw_paragraph(c, text, x, y, width, fontName, fontSize, color, leading=None):
    if leading is None:
        leading = fontSize * 1.4
    style = ParagraphStyle(
        name='CustomStyle',
        fontName=fontName,
        fontSize=fontSize,
        textColor=color,
        leading=leading,
        alignment=0 # Left align
    )
    p = Paragraph(text, style)
    w, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return y - h

def generate_v8_final_manifesto():
    file_path = "ORACLE_DEAD_ZONE_REPORT.pdf"
    c = canvas.Canvas(file_path, pagesize=LETTER)
    width, height = LETTER

    # Brand Colors
    obsidian = HexColor("#020617")
    midnight = HexColor("#0f172a")
    oracle_blue = HexColor("#38bdf8")
    emerald = HexColor("#10b981")
    cloud_white = HexColor("#f8fafc")
    slate_grey = HexColor("#94a3b8")
    crimson = HexColor("#ef4444")
    gold = HexColor("#f59e0b")

    # --- PAGE 1: THE COVER ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    c.setStrokeColor(oracle_blue); c.setLineWidth(0.5); c.setStrokeAlpha(0.08)
    for x in range(0, int(width), 30): c.line(x, 0, x, height)
    for y in range(0, int(height), 30): c.line(0, y, width, y)
    c.setStrokeAlpha(1.0)
    c.setFont("Helvetica-Bold", 55); c.setFillColor(cloud_white)
    c.drawString(1*inch, height - 3*inch, "THE DEAD")
    c.drawString(1*inch, height - 3.8*inch, "ZONE REPORT")
    c.setStrokeColor(oracle_blue); c.setLineWidth(4); c.line(1*inch, height - 4.2*inch, 4.5*inch, height - 4.2*inch)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(oracle_blue)
    c.drawString(1*inch, height - 4.8*inch, "A Technical Abstract on Mathematical")
    c.drawString(1*inch, height - 5.1*inch, "Variance and Structural Deployment")
    c.setFont("Helvetica", 14); c.setFillColor(slate_grey)
    c.drawString(1*inch, height - 6.5*inch, "James McCabe | ModernCYPH3R.com")
    c.drawString(1*inch, height - 6.8*inch, "Date: March 25, 2026")
    
    # "TOP SECRET" stamp overlay
    c.saveState()
    c.translate(width - 3.5*inch, height - 2*inch)
    c.rotate(15)
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(crimson)
    c.setStrokeColor(crimson)
    c.setLineWidth(2)
    c.rect(-0.2*inch, -0.2*inch, 2.8*inch, 0.6*inch)
    c.drawString(0, 0, "RESTRICTED")
    c.restoreState()

    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 2: THE RANDOMNESS PARADOX ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.2*inch, "01. THE RANDOMNESS PARADOX")
    
    y = height - 1.6*inch
    copy1 = """
    <font size="12">Let's address the elephant in the room: <b>"AI Lottery Predictors."</b></font><br/><br/>
    We recently disassembled one of the leading "AI" prediction apps on the market. We reverse-engineered their binary. There was no neural network. There was no machine learning. Under the hood, it was executing a basic Javascript <i>Math.random()</i> function.<br/><br/>
    It was a black-box slot machine wrapped in marketing snake oil. They sell you the illusion of intelligence; they deliver the exact same random trash the state terminal gives you.<br/><br/>
    <b>The Oracle does not use "fake AI" to predict the future. It uses deterministic combinatorial mathematics to manage the present.</b><br/><br/>
    The lottery is a game of pure mathematical variance. Most participants attempt to defeat this with "luck." They use birthdays, anniversaries, or—the most lethal error—the automated <b>Quick Pick</b>.<br/><br/>
    The state relies on your lack of discipline. Random Number Generators are mathematically blind. They populate every possible combination in the matrix, regardless of how statistically invisible it is in a human lifetime. Randomness ensures a flat distribution where 50% of every dollar is retained without a fight.<br/><br/>
    The Oracle is the structural antidote. We do not predict the future; we identify where the future is most likely to occur. We treat the lottery like a technical deployment, not a game of chance. If you are going to play, you must involve math to give yourself a fighting chance on solid footing.
    """
    y = draw_paragraph(c, copy1, 0.75*inch, y, 7*inch, "Helvetica", 11, cloud_white)
    
    c.setFillColor(HexColor("#450a0a")); c.rect(0.75*inch, y - 0.8*inch, 7*inch, 0.6*inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f87171")); c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, y - 0.5*inch, "INDUSTRIAL REALITY: THE QUICK PICK IS A VOLUNTARY TAX.")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 3: CENTER OF MASS ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.2*inch, "02. THE MATHEMATICAL CENTER OF MASS")
    
    y = height - 1.6*inch
    copy2a = """
    <b>PART A: THE STARTING NUMBER SPATIAL ANOMALY</b><br/><br/>
    In Powerball, only <b>17.8%</b> of draws start with a number greater than 20. In Mega Millions, it's a brutal <b>7.1%</b>.<br/><br/>
    If your ticket starts with a 25, you have immediately exiled yourself to a statistical wasteland. You are paying for a ticket that is <i>mathematically dead on arrival</i>. The Oracle's Pattern Scouter physically prevents these anomalies from entering your deployment sequence.
    """
    y = draw_paragraph(c, copy2a, 0.75*inch, y, 7*inch, "Helvetica", 11, cloud_white)

    # Chart A
    chart_y = y - 1.6*inch
    c.setFillColor(oracle_blue); c.rect(2.5*inch, chart_y, 1*inch, 1.2*inch, fill=1)
    c.setFillColor(cloud_white); c.setFont("Helvetica-Bold", 10); c.drawCentredString(3.0*inch, chart_y + 1.3*inch, "17.8%")
    c.drawCentredString(3.0*inch, chart_y - 0.2*inch, "Powerball")
    c.setFillColor(crimson); c.rect(4.5*inch, chart_y, 1*inch, 0.4*inch, fill=1)
    c.setFillColor(cloud_white); c.drawCentredString(5.0*inch, chart_y + 0.5*inch, "7.1%")
    c.drawCentredString(5.0*inch, chart_y - 0.2*inch, "Mega Millions")
    c.saveState(); c.translate(1.0*inch, chart_y + 0.1*inch); c.rotate(90)
    c.setFont("Helvetica-Bold", 9); c.setFillColor(slate_grey); c.drawString(0, 0, "Prob of Start Number > 20"); c.restoreState()

    y = chart_y - 0.8*inch
    copy2b = """
    <br/><b>PART B: THE CASH GAME CLASSIFICATION (GRAVITY)</b><br/><br/>
    In smaller matrix games like Cash 5 (VA/TX), the gravity is extreme. With only 45 balls, the math forces a heavy cluster at the low end. <b>74.4% of draws start between 1 and 10.</b><br/><br/>
    When you play a Cash 5 game, the 'Center of Mass' is violently skewed. Your starting number is the anchor; if the anchor is misplaced, the entire sequence collapses under the weight of variance.
    """
    y = draw_paragraph(c, copy2b, 0.75*inch, y, 7*inch, "Helvetica", 11, cloud_white)
    
    # Chart B (Cash 5 Gravity Histogram)
    chart_y2 = y - 1.8*inch
    c.setStrokeColor(slate_grey); c.setLineWidth(1)
    c.line(2*inch, chart_y2, 6*inch, chart_y2) # X axis
    c.line(2*inch, chart_y2, 2*inch, chart_y2 + 1.5*inch) # Y axis
    
    # Bars (1-10, 11-20, 21-30, 31+)
    heights = [1.2, 0.4, 0.1, 0.05]
    labels = ["1-10", "11-20", "21-30", "31+"]
    colors_bars = [emerald, gold, crimson, crimson]
    pcts = ["74.4%", "20.1%", "4.3%", "1.2%"]
    
    x_pos = 2.2*inch
    for i in range(4):
        c.setFillColor(colors_bars[i])
        c.rect(x_pos, chart_y2, 0.6*inch, heights[i]*inch, fill=1, stroke=0)
        c.setFillColor(cloud_white); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x_pos + 0.3*inch, chart_y2 + heights[i]*inch + 0.05*inch, pcts[i])
        c.setFillColor(slate_grey); c.setFont("Helvetica", 8)
        c.drawCentredString(x_pos + 0.3*inch, chart_y2 - 0.15*inch, labels[i])
        x_pos += 0.9*inch

    c.saveState(); c.translate(1.7*inch, chart_y2 + 0.2*inch); c.rotate(90)
    c.setFont("Helvetica-Bold", 8); c.setFillColor(slate_grey); c.drawString(0, 0, "Frequency"); c.restoreState()
    c.drawCentredString(4*inch, chart_y2 - 0.4*inch, "Starting Number Ranges (Cash 5)")

    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 4: MATH LESSON & PICK 3 ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.2*inch, "03. COMBINATORIAL SPREAD VS. SUM DISTRIBUTION")
    
    y = height - 1.6*inch
    copy3 = """
    <b>Combinatorial Math (Powerball/Lotto/Cash 5):</b> Deals with 'Sampling Without Replacement'—the exact order of the balls doesn't matter, but the <b>spatial spread</b> (the physical gaps between numbers) is everything. We look at 'Triplets' and mathematical clustering to ensure coverage across the entire matrix.<br/><br/>
    <b>Sum Distribution (Pick 3/Pick 4/Pick 5):</b> Deals with 'Sampling With Replacement'—order is king. We use Sum Distribution to find the Mathematical Center of Mass. In Pick 3, for instance, there are 1,000 possible permutations (000 to 999). However, they are forced to cluster around the median sums by the sheer volume of mathematical combinations.
    """
    y = draw_paragraph(c, copy3, 0.75*inch, y, 7*inch, "Helvetica", 11, cloud_white)

    # Bell Curve with Dead Zones
    y_curve = y - 3.2*inch
    
    # Background axis
    c.setStrokeColor(slate_grey); c.setLineWidth(1)
    c.line(1.0*inch, y_curve, 7.5*inch, y_curve)
    
    # Draw Dead Zone (Left)
    c.setFillAlpha(0.5); c.setFillColor(HexColor("#450a0a")); c.rect(1.0*inch, y_curve, 1.8*inch, 2.2*inch, fill=1, stroke=0); c.setFillAlpha(1.0)
    c.setFillColor(crimson); c.setFont("Helvetica-Bold", 10); c.drawString(1.1*inch, y_curve + 2.0*inch, "DEAD ZONE")
    c.setFont("Helvetica", 8); c.drawString(1.1*inch, y_curve + 1.85*inch, "Sums 0-5 (Highly Improbable)")

    # Draw Center of Mass (Center)
    c.setFillAlpha(0.5); c.setFillColor(HexColor("#064e3b")); c.rect(3.2*inch, y_curve, 2.1*inch, 2.2*inch, fill=1, stroke=0); c.setFillAlpha(1.0)
    c.setFillColor(emerald); c.setFont("Helvetica-Bold", 10); c.drawCentredString(4.25*inch, y_curve + 2.0*inch, "CENTER OF MASS")
    c.setFont("Helvetica", 8); c.drawCentredString(4.25*inch, y_curve + 1.85*inch, "Sums 13-15 (Target Pocket)")

    # Draw Dead Zone (Right)
    c.setFillAlpha(0.5); c.setFillColor(HexColor("#450a0a")); c.rect(5.7*inch, y_curve, 1.8*inch, 2.2*inch, fill=1, stroke=0); c.setFillAlpha(1.0)
    c.setFillColor(crimson); c.setFont("Helvetica-Bold", 10); c.drawString(5.8*inch, y_curve + 2.0*inch, "DEAD ZONE")
    c.setFont("Helvetica", 8); c.drawString(5.8*inch, y_curve + 1.85*inch, "Sums 22-27 (Statistically Dead)")

    # The Curve
    c.setStrokeColor(oracle_blue); c.setLineWidth(3)
    p = c.beginPath(); p.moveTo(1.0*inch, y_curve)
    # Control points to make a nice bell curve over the ranges
    p.curveTo(2.5*inch, y_curve, 3.5*inch, y_curve + 2.0*inch, 4.25*inch, y_curve + 2.0*inch)
    p.curveTo(5.0*inch, y_curve + 2.0*inch, 6.0*inch, y_curve, 7.5*inch, y_curve); c.drawPath(p)

    c.setFillColor(midnight); c.rect(0.75*inch, y_curve - 1.8*inch, 7*inch, 1.2*inch, fill=1, stroke=1)
    c.setStrokeColor(emerald); c.setFillColor(oracle_blue); c.setFont("Helvetica-Bold", 12)
    c.drawString(1.0*inch, y_curve - 0.9*inch, "THE TECHNICIAN'S CREED:")
    c.setFont("Helvetica", 10.5); c.setFillColor(cloud_white)
    c.drawString(1.0*inch, y_curve - 1.15*inch, "Stop guessing. The Oracle is a heavy-duty industrial sieve designed to filter out the")
    c.drawString(1.0*inch, y_curve - 1.35*inch, "statistical trash. We play the center of gravity where history actually happens.")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 5: THE ASSEMBLY LINE ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.1*inch, "04. THE ORACLE ASSEMBLY LINE")
    c.setFont("Helvetica", 11); c.drawString(0.75*inch, height - 1.5*inch, "We do not predict. We architect. The flow from 10-year history to deployment is a technical sequence.")
    
    start_y = height - 2.5*inch
    
    # Re-engineered Flow Blocks
    block_width = 1.35*inch
    block_gap = 0.4*inch
    current_x = 0.75*inch

    flow_stages = [
        ("THE PROPHET", oracle_blue),
        ("THE PRAGMATIST", gold),
        ("PATTERN SCOUTER", crimson),
        ("THE VAULT", emerald)
    ]

    for title, color in flow_stages:
        c.setFillColor(midnight); c.setStrokeColor(color); c.setLineWidth(1.5)
        c.rect(current_x, start_y, block_width, 0.4*inch, fill=1, stroke=1)
        c.setFillColor(cloud_white); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(current_x + block_width/2, start_y + 0.15*inch, title)
        
        # Draw arrow if not the last block
        if current_x < 5.5*inch:
            c.setStrokeColor(slate_grey); c.setLineWidth(1)
            c.line(current_x + block_width + 0.05*inch, start_y + 0.2*inch, current_x + block_width + block_gap - 0.05*inch, start_y + 0.2*inch)
            # Arrowhead
            c.line(current_x + block_width + block_gap - 0.1*inch, start_y + 0.25*inch, current_x + block_width + block_gap - 0.05*inch, start_y + 0.2*inch)
            c.line(current_x + block_width + block_gap - 0.1*inch, start_y + 0.15*inch, current_x + block_width + block_gap - 0.05*inch, start_y + 0.2*inch)
        
        current_x += block_width + block_gap

    y = start_y - 0.6*inch
    copy_engine = """
    <b>1. THE PROPHET (Markov Chains & Poisson Tension)</b><br/>
    Reads the 10-year historical flow. Models the 'State Machine' of the draw. If ball 14 hit tonight, what ball mathematically follows it historically? It tracks Base Frequency and identifies clusters that are statistically 'due' based on Poisson deviation.<br/><br/>
    <b>2. THE PRAGMATIST (Combinatorial Wheeling)</b><br/>
    The deployment tool. It uses Greedy Wheeling Algorithms to optimize your physical coverage. If our core 'Smart Pool' contains the winning numbers, the Pragmatist ensures the tickets are structured to capture multiple secondary prizes (4-of-5, 3-of-5) to fund your campaign.<br/><br/>
    <b>3. THE PATTERN SCOUTER (The Final Bouncer)</b><br/>
    Enforces spatial filters (rejects clusters that are too tight or too wide), odd/even ratios (forces the 3:2 or 2:3 reality), limits consecutive sequences, and purges historical collisions to ensure you never play a jackpot that has already hit in the last 20 years.<br/><br/>
    <b>4. THE VAULT (Output)</b><br/>
    The hardened deployment sequence. Ready for physical or digital execution via the dashboard.
    """
    y = draw_paragraph(c, copy_engine, 0.75*inch, y, 7*inch, "Helvetica", 11, cloud_white)

    c.setFillColor(midnight); c.rect(0.75*inch, y - 1.4*inch, 7*inch, 1.0*inch, fill=1, stroke=1)
    c.setStrokeColor(oracle_blue); c.setFillColor(oracle_blue); c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, y - 0.7*inch, "CRITICAL PROTOCOL: NOT A LOTTERY PREDICTOR")
    c.setFont("Helvetica", 10); c.setFillColor(cloud_white)
    c.drawCentredString(width/2, y - 1.0*inch, "The Oracle manages the distribution of your play against statistical noise.")
    c.drawCentredString(width/2, y - 1.25*inch, "It cannot predict future events, only eliminate the 70% of reality that will never occur.")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 6: THE COMMAND ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    
    # TITLE (Y=9.8")
    c.setFont("Helvetica-Bold", 30); c.setFillColor(cloud_white)
    c.drawCentredString(width/2, height - 1.2*inch, "INITIALIZE THE PROTOCOL")
    
    # VAULT TEXT (Y=9.2")
    y_cta = height - 1.8*inch
    copy_cta = """
    <div align="center">
    You are now standing at the threshold of the Vault. The data you have read is the map; the Oracle is the vehicle.<br/><br/>
    Most will continue to play the Quick Pick donation game. A small syndicate of technicians will choose to play with structural mathematical footing.<br/><br/>
    The Vault is initialized. The data is current. The choice is yours.
    </div>
    """
    draw_paragraph(c, copy_cta, 1.0*inch, y_cta, 6.5*inch, "Helvetica", 12, cloud_white)
    
    # PRO TIER ACTIVATION BOX (SHIFTED DOWN TO Y=3.5", HEIGHT=3.9")
    # This pushes the top of the box to 7.4", leaving a massive 1.8" gap below the Vault Text.
    pro_box_y = 3.5*inch
    pro_box_height = 3.9*inch
    c.setFillColor(midnight); c.rect(1.25*inch, pro_box_y, 6.0*inch, pro_box_height, fill=1, stroke=1)
    c.setStrokeColor(oracle_blue); c.setFont("Helvetica-Bold", 16); c.setFillColor(oracle_blue)
    c.drawString(1.5*inch, pro_box_y + pro_box_height - 0.4*inch, "PRO TIER ACTIVATION:")
    
    # PERKS STARTING AT Y=6.6"
    y_perks = pro_box_y + pro_box_height - 0.8*inch
    copy_perks = """
    • <b>50 Daily High-Volume Generations</b> across all state and national sectors.<br/><br/>
    • <b>Advanced Markov Transition Dashboards</b> & Overdue Poisson Tension Graphs.<br/><br/>
    • <b>Professional Syndicate PDF Manifests</b> for multi-user deployment tracking.<br/><br/>
    • <b>Real-Time API Ingestion</b> supporting National games (PB/MM) plus VA, NY, TX, and CA.<br/><br/>
    • <b>Weekly Matrix Expansions</b> rapidly bringing new states online to ensure your sector is covered.
    """
    draw_paragraph(c, copy_perks, 1.7*inch, y_perks, 5.0*inch, "Helvetica", 11, cloud_white)
    
    # FINAL CALL TO ACTION (SHIFTED DOWN TO Y=3.0")
    y_final_cta = 3.0*inch
    copy_final = """
    <div align="center">
    <b>Test the architecture for yourself.</b> The Free Tier allows for 5 combinatorial generations per day. 
    Verify the math. See the spatial filters in real-time. Once you understand the gravity of what we've built, 
    upgrade to the Pro Tier and deploy at scale.
    </div>
    """
    draw_paragraph(c, copy_final, 1.0*inch, y_final_cta, 6.5*inch, "Helvetica", 11, slate_grey)

    # DEPLOY AT BUTTON (SHIFTED DOWN TO Y=1.3")
    btn_y = 1.3*inch
    c.setFillColor(midnight); c.rect(width/2 - 2.5*inch, btn_y, 5*inch, 0.6*inch, fill=1, stroke=1)
    c.setStrokeColor(emerald); c.setFillColor(emerald); c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, btn_y + 0.2*inch, "DEPLOY AT: ORACLEAPP.MODERNCYPH3R.COM")
    
    draw_footer(c, width, height, slate_grey); c.showPage()
    c.save()
    print("Industrial Manifesto v8.6 generated: ORACLE_DEAD_ZONE_REPORT.pdf")

if __name__ == "__main__":
    generate_v8_final_manifesto()
