class GameConfig:
    # Points awarded when both players cooperate
    MUTUAL_COOPERATION_POINTS = 4
    
    # Points awarded to defector when other player cooperates
    BETRAYAL_POINTS = 6
    
    # Points awarded to player who got betrayed
    BETRAYED_POINTS = 0
    
    # Points awarded when both players defect
    MUTUAL_DEFECTION_POINTS = 2
    
    # Default number of rounds per match
    NUMBER_OF_ROUNDS = 200

    # Whether to add noise to number of rounds
    ADD_NOISE = False