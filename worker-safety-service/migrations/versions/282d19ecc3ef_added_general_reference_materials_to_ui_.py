"""added_general_reference_materials_to_ui_config_table

Revision ID: 282d19ecc3ef
Revises: 5da8ea01f998
Create Date: 2024-09-18 12:58:54.385491

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "282d19ecc3ef"
down_revision = "7bb43cc3b89e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = jsonb_set(
            contents,
            '{general_reference_materials}',
            '[
                {"id": 1, "name": "Commercial Driver License (CDL) Training Videos" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/CDL.aspx"},
                {"id": 2, "name": "Electric T&D Training Videos" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/td_videos.aspx"},
                {"id": 3, "name": "Ergo-Power Safety Videos" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/ergo_power.aspx"},
                {"id": 4, "name": "Clearance & Control (EOP G014) Learning Modules" ,  "link": "https://nationalgridplc.sharepoint.com/:u:/r/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/Clearance-%26-Control-modules.aspx?csf=1&web=1&e=XOqSfz"},
                {"id": 5, "name": "Reenactment Videos" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-EXT-US-NationalGridUSAcademy/SitePages/IncidentAnimationVideos.aspx"},
                {"id": 6, "name": "Safety Training Videos" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/SitePages/safety_videos.aspx"},
                {"id": 7, "name": "Code Blue" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-USAcademyDocumentStore/AcadRes/VILT/General%20Training%20Videos/Code%20Blue%20System%20Activation.mp4?web=1"},
                {"id": 8, "name": "Safety Policies and Procedures" , "link": "https://gridhome.nationalgrid.com/sites/safety-us/SitePageModern/81778/policies-and-procedures"},
                {"id": 9, "name": "Employee Safety Handbook" , "link": "https://gridhome.nationalgrid.com/redir/116974"},
                {"id": 10, "name": "Cargo Securement Manual" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fCargo+Securement+Manual.pdf"},
                {"id": 11, "name": "Q1702 Work Zone Traffic Control" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fQ1702-Work+Zone+Traffic+Control.pdf"},
                {"id": 12, "name": "Work Zone Traffic Control Manual" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fWork+Zone+Traffic+Control+Manual.pdf"},
                {"id": 13, "name": "A-105 Job Briefing Procedure" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fA105-Job+Briefing.pdf"},
                {"id": 14, "name": "Heat Illness Prevention Procedure" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fHeat+Illness+Prevention+Procedure.pdf"},
                {"id": 15, "name": "C-301 Ladder Safety" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fC301-Ladder+Safety.pdf"},
                {"id": 16, "name": "E504 Material Handling and Rigging" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fE504-Material+Handling+and+Rigging+Equipment.pdf"},
                {"id": 17, "name": "H806 Fall Protection" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fH806-Fall+Protection.pdf"},
                {"id": 18, "name": "PPE Hazard Assessment H-801" , "link": "https://gridhome.nationalgrid.com/documentredirect/?url=https%3a%2f%2fnationalgridplc.sharepoint.com%2fsites%2fgridhome-ng%2fDocuments%2fH801-Protective+Equipment+and+Hazard+Assessment.pdf"},
                {"id": 19, "name": "PPE Catalog" , "link": "https://gridhome.nationalgrid.com/redir/116732"},
                {"id": 20, "name": "Code Blue Activation" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-US-ElectricWorkMethods/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FGRP%2DINT%2DUS%2DElectricWorkMethods%2FShared%20Documents%2FEOPs%20OH%2C%20UG%2C%20Distr%20and%20Transm%2FNG%2DEOP%20G027%2Epdf&parent=%2Fsites%2FGRP%2DINT%2DUS%2DElectricWorkMethods%2FShared%20Documents%2FEOPs%20OH%2C%20UG%2C%20Distr%20and%20Transm&p=true&wdLOR=c921F34CA%2D97E4%2D47D3%2D93E6%2D63C7725CC691&ga=1"},
                {"id": 21, "name": "Safety Data Sheet" , "link": "https://www.3eonline.com/EeeOnlinePortal/DesktopDefault.aspx?id=HaXQ%2bQ9l4S%2b1Uh7ciWUqBk9UdVcEKfM2cO4ZyO5us28%3d"},
                {"id": 22, "name": "Minimum Approach Distance (MAD) for voltages above 2.5kV" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-US-ElectricWorkMethods/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FGRP%2DINT%2DUS%2DElectricWorkMethods%2FShared%20Documents%2FBulletins%20WM%2C%20Stds%20Bulletins%20and%20Tool%2FWM%20Bulletin%20%2324%2D01%2Epdf&parent=%2Fsites%2FGRP%2DINT%2DUS%2DElectricWorkMethods%2FShared%20Documents%2FBulletins%20WM%2C%20Stds%20Bulletins%20and%20Tool&p=true&wdLOR=cB6DB402A%2D1F90%2D4FD3%2DBE47%2DA15FA78F3A25&ga=1"},
                {"id": 23, "name": "Minimum Approach Distance (MAD) for Voltages Above 72.5kV New York Workers" , "link": "https://nationalgridplc.sharepoint.com/sites/GRP-INT-US-ElectricWorkMethods/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FGRP%2DINT%2DUS%2DElectricWorkMethods%2FShared%20Documents%2FBulletins%20WM%2C%20Stds%20Bulletins%20and%20Tool%2FWork%20Methods%20Bulletin%2023%2D11%2Epdf&parent=%2Fsites%2FGRP%2DINT%2DUS%2DElectricWorkMethods%2FShared%20Documents%2FBulletins%20WM%2C%20Stds%20Bulletins%20and%20Tool&p=true&wdLOR=c20AFA385%2D5A83%2D4517%2D8C78%2D927F765B2B59&ga=1"}
            ]'::jsonb
        )
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )


def downgrade() -> None:
    op.execute(
        """
            UPDATE uiconfigs
            SET contents = contents::jsonb - '{general_reference_materials}'
            WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )
