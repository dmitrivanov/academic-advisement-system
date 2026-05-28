const MAJORS = {
  "CS": {
    "courses": {
      "CSC 101": {
        "title": "Principles in Information Technology and Computation",
        "credits": 3,
        "prereqs": [],
        "alternatives": []
      },
      "CSC 111": {
        "title": "Introduction to Programming",
        "credits": 4,
        "prereqs": [
          "CSC 101",
          "MAT 206"
        ],
        "alternatives": []
      },
      "CSC 211": {
        "title": "Advanced Programming Techniques",
        "credits": 3,
        "prereqs": [
          "CSC 111"
        ],
        "alternatives": []
      },
      "CSC 215": {
        "title": "Fundamentals of Computer Systems",
        "credits": 3,
        "prereqs": [
          "CSC 111"
        ],
        "alternatives": []
      },
      "CSC 231": {
        "title": "Discrete Structures and Applications to Computer Science",
        "credits": 4,
        "prereqs": [
          "CSC 111",
          "MAT 301"
        ],
        "alternatives": []
      },
      "CSC 331": {
        "title": "Data Structures",
        "credits": 3,
        "prereqs": [
          "CSC 211",
          "CSC 231"
        ],
        "alternatives": []
      },
      "CSC 350": {
        "title": "Software Development",
        "credits": 3,
        "prereqs": [
          "CSC 211"
        ],
        "alternatives": []
      },
      "MAT 206": {
        "title": "Precalculus",
        "credits": 4,
        "prereqs": [],
        "alternatives": [
          "MAT 301"
        ]
      },
      "MAT 301": {
        "title": "Analytic Geometry and Calculus I",
        "credits": 4,
        "prereqs": [
          "MAT 206"
        ],
        "alternatives": []
      },
      "MAT 302": {
        "title": "Analytic Geometry and Calculus II",
        "credits": 4,
        "prereqs": [
          "MAT 301"
        ],
        "alternatives": []
      }
    },
    "layout": [
      [
        "CSC 101",
        "MAT 206"
      ],
      [
        "CSC 111",
        "MAT 301"
      ],
      [
        "CSC 211",
        "CSC 215",
        "CSC 231",
        "MAT 302"
      ],
      [
        "CSC 331",
        "CSC 350"
      ]
    ],
    "name": "Computer Science"
  },
  "CIS": {
    "courses": {
      "ACC 122": {
        "title": "Accounting Principles I",
        "credits": 3,
        "prereqs": [],
        "alternatives": []
      },
      "BUS 104": {
        "title": "Introduction to Business",
        "credits": 3,
        "prereqs": [],
        "alternatives": []
      },
      "CSC 101": {
        "title": "Principles in Information Technology and Computation",
        "credits": 3,
        "prereqs": [],
        "alternatives": []
      },
      "CSC 110": {
        "title": "Computer Programming I",
        "credits": 4,
        "prereqs": [
          "CSC 101"
        ],
        "alternatives": [
          "CSC 111"
        ]
      },
      "CSC 210": {
        "title": "Computer Programming II",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "CIS 345": {
        "title": "Telecommunication Network I",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "CIS 385": {
        "title": "Web Programming I",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "CIS 395": {
        "title": "Database System I",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "CIS 440": {
        "title": "Unix",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "CIS 485": {
        "title": "Web Programming II",
        "credits": 3,
        "prereqs": [
          "CIS 385",
          "CSC 210"
        ],
        "alternatives": []
      },
      "CIS 495": {
        "title": "Database System II",
        "credits": 3,
        "prereqs": [
          "CIS 395"
        ],
        "alternatives": []
      },
      "PHY 110": {
        "title": "General Physics",
        "credits": 4,
        "prereqs": [],
        "alternatives": [
          "AST 110"
        ]
      },
      "MAT 206": {
        "title": "Precalculus",
        "credits": 4,
        "prereqs": [],
        "alternatives": [
          "MAT 301"
        ]
      }
    },
    "layout": [
      [
        "ACC 122",
        "BUS 104",
        "CSC 101",
        "MAT 206",
        "PHY 110"
      ],
      [
        "CIS 345",
        "CIS 385",
        "CIS 395",
        "CIS 440",
        "CSC 110",
        "CSC 210"
      ],
      [
        "CIS 485",
        "CIS 495"
      ]
    ],
    "name": "Computer Information Systems"
  },
  "CNT": {
    "courses": {
      "CSC 101": {
        "title": "Principles in Information Technology and Computation",
        "credits": 3,
        "prereqs": [],
        "alternatives": []
      },
      "CSC 110": {
        "title": "Computer Programming I",
        "credits": 4,
        "prereqs": [],
        "alternatives": [
          "CSC 111"
        ]
      },
      "CIS 165": {
        "title": "Introduction to Operating Systems",
        "credits": 3,
        "prereqs": [
          "CSC 101"
        ],
        "alternatives": []
      },
      "CIS 255": {
        "title": "Computer Software",
        "credits": 3,
        "prereqs": [
          "CIS 165"
        ],
        "alternatives": []
      },
      "CIS 345": {
        "title": "Telecommunication Network I",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "CIS 445": {
        "title": "Telecommunication Network II / LAN",
        "credits": 3,
        "prereqs": [
          "CIS 345"
        ],
        "alternatives": []
      },
      "CIS 455": {
        "title": "Network Security",
        "credits": 3,
        "prereqs": [
          "CIS 345"
        ],
        "alternatives": []
      },
      "CIS 440": {
        "title": "Unix",
        "credits": 3,
        "prereqs": [
          [
            "CSC 110",
            "CSC 111"
          ]
        ],
        "alternatives": []
      },
      "PHY 110": {
        "title": "General Physics",
        "credits": 4,
        "prereqs": [],
        "alternatives": [
          "AST 110"
        ]
      },
      "MAT 206": {
        "title": "Precalculus",
        "credits": 4,
        "prereqs": [],
        "alternatives": [
          "MAT 301"
        ]
      }
    },
    "layout": [
      [
        "CSC 101",
        "CSC 110",
        "MAT 206",
        "PHY 110"
      ],
      [
        "CIS 165",
        "CIS 345",
        "CIS 440"
      ],
      [
        "CIS 255",
        "CIS 445",
        "CIS 455"
      ]
    ],
    "name": "Computer Network Technology"
  }
};
