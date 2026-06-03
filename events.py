EVENT_NAMES = {
    # FNCS
    "showdowntournament_fncs_npm_trios": "FNCS - Trios (NPM)",
    "showdowntournament_fncs_pbm_duos": "FNCS - Duos (PBM)",
    # Ranked / RC
    "showdowntournament_rc_solo": "Ranked Cup - Solo",
    "showdowntournament_rc_duos": "Ranked Cup - Duos",
    "showdowntournament_rc_squads": "Ranked Cup - Squads",
    "showdowntournament_rc_dashberryduo_nofill": "Ranked Cup - Dashberry Duos",
    # NPM / General
    "showdowntournament_npm_duos": "Tournament - Duos (NPM)",
    "showdowntournament_npm_trios": "Tournament - Trios (NPM)",
    "showdowntournament_solo": "Typical Gamer Icon Cup - Solo",
    "showdowntournament_duos": "Tournament - Duos",
    "showdowntournament_trios": "Tournament - Trios",
    "showdowntournament_squads": "Tournament - Squads",
    # Dashberry
    "showdowntournament_dashberryduo_cr": "Dashberry Cup - Duos (CR)",
    "showdowntournament_dashberryduo_nofill": "Dashberry Cup - Duos (No Fill)",
    "showdowntournament_dashberryduo_rc": "Dashberry Cup - Duos (RC)",
    # Blastberry
    "showdowntournament_blastberryduo_nofill": "Blastberry Cup - Duos",
    "showdowntournament_blastberrysquad_nofill": "Blastberry Cup - Squads",
    # Figment
    "showdowntournament_figmentduo": "Figment Cup - Duos",
    "showdowntournament_figmentsquad": "Figment Cup - Squads",
    # Sourspawn
    "showdowntournament_sourspawnduos": "Sourspawn Cup - Duos",
    # Rematch
    "showdowntournament_re_matchmistduos_cr": "Rematch - Matchmist Duos (CR)",
    # No Build
    "showdowntournament_nobuildbr_duos": "Zero Build Cup - Duos",
    "showdowntournament_nobuildbr_trios": "Zero Build Cup - Trios",
    # Clyde
    "showdowntournament_clyde_solo": "Clyde Cup - Solo",
    "showdowntournament_clyde_trios": "Clyde Cup - Trios",
    # Punchberry
    "showdowntournament_punchberryduo_nofill": "Punchberry Cup - Duos",
    # Habanero ranked
    "habanerosolo": "Ranked - Solo",
    "habaneroduo": "Ranked - Duos",
    "habanerotrio": "Ranked - Trios",
    "habanerosquad": "Ranked - Squads",
}

PLAYLIST_FORMAT = {
    "solo": "Solo",
    "duos": "Duo",
    "duo": "Duo",
    "trios": "Trio",
    "trio": "Trio",
    "squads": "Squad",
    "squad": "Squad",
    "nofill": "Duo (No Fill)",
}


def get_event_name(code: str) -> str:
    return EVENT_NAMES.get(code, code.replace("_", " ").title())


def get_roster_format(code: str) -> str:
    code_lower = code.lower()
    for keyword, label in PLAYLIST_FORMAT.items():
        if keyword in code_lower:
            return label
    return "Unknown"
