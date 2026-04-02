    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 6: THE COMMAND ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 30); c.setFillColor(cloud_white); c.drawCentredString(width/2, height - 2.5*inch, "INITIALIZE THE PROTOCOL")
    
    y_cta = height - 3.2*inch
    copy_cta = """
    <div align="center">
    You are now standing at the threshold of the Vault. The data you have read is the map; the Oracle is the vehicle.<br/><br/>
    Most will continue to play the Quick Pick donation game. A small syndicate of technicians will choose to play with structural mathematical footing.<br/><br/>
    The Vault is initialized. The data is current. The choice is yours.
    </div>
    """
    draw_paragraph(c, copy_cta, 1.0*inch, y_cta, 6.5*inch, "Helvetica", 12, cloud_white)
    
    # PRO TIER ACTIVATION BOX
    pro_box_y = 3.5*inch
    pro_box_height = 2.4*inch
    c.setFillColor(midnight); c.rect(1.25*inch, pro_box_y, 6.0*inch, pro_box_height, fill=1, stroke=1)
    c.setStrokeColor(oracle_blue); c.setFont("Helvetica-Bold", 16); c.setFillColor(oracle_blue)
    c.drawString(1.5*inch, pro_box_y + pro_box_height - 0.4*inch, "PRO TIER ACTIVATION:")
    
    y_perks = pro_box_y + pro_box_height - 0.7*inch
    copy_perks = """
    • <b>50 Daily High-Volume Generations</b> across all state and national sectors.<br/><br/>
    • <b>Advanced Markov Transition Dashboards</b> & Overdue Poisson Tension Graphs.<br/><br/>
    • <b>Professional Syndicate PDF Manifests</b> for multi-user deployment tracking.<br/><br/>
    • <b>Real-Time API Ingestion</b> for NAT (PB/MM), VA, NY, TX, and CA games.<br/><br/>
    • <b>Weekly Matrix Expansions</b> ensuring your sector is always covered.
    """
    draw_paragraph(c, copy_perks, 1.7*inch, y_perks, 5.0*inch, "Helvetica", 11, cloud_white)
    
    # FINAL CALL TO ACTION
    y_final_cta = pro_box_y - 0.5*inch
    copy_final = """
    <div align="center">
    <b>Test the architecture for yourself.</b> The Free Tier allows for 5 combinatorial generations per day.<br/>
    Verify the math. See the spatial filters in real-time. Once you understand the gravity of what we've built,<br/>
    upgrade to the Pro Tier and deploy at scale.
    </div>
    """
    draw_paragraph(c, copy_final, 1.0*inch, y_final_cta, 6.5*inch, "Helvetica", 11, slate_grey)

    # DEPLOY AT BUTTON
    btn_y = y_final_cta - 1.2*inch
    c.setFillColor(midnight); c.rect(width/2 - 2.5*inch, btn_y, 5*inch, 0.6*inch, fill=1, stroke=1)
    c.setStrokeColor(emerald); c.setFillColor(emerald); c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, btn_y + 0.2*inch, "DEPLOY AT: ORACLEAPP.MODERNCYPH3R.COM")
    
    draw_footer(c, width, height, slate_grey); c.save()
    print("Industrial Manifesto v8.2 generated: ORACLE_DEAD_ZONE_REPORT.pdf")

if __name__ == "__main__":
    generate_v8_final_manifesto()
