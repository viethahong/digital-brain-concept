const BRAIN_STATS = {
    "knowledge": {
        "1_Biet": 0,
        "2_Hieu": 1,
        "3_Hanh": 0,
        "4_Thong": 0,
        "5_Tue": 0,
        "files": [
            {
                "title": "Deep Work",
                "path": "wiki/01_knowledge/deep-work.md",
                "level": "2_Hieu"
            }
        ]
    },
    "principles": {
        "1_Biet": 0,
        "2_Hieu": 0,
        "3_Hanh": 1,
        "4_Thong": 0,
        "5_Tue": 0,
        "files": [
            {
                "title": "Pareto Principle",
                "path": "wiki/02_principles/pareto-principle.md",
                "level": "3_Hanh"
            }
        ]
    },
    "philosophies": {
        "1_Biet": 1,
        "2_Hieu": 1,
        "3_Hanh": 0,
        "4_Thong": 0,
        "5_Tue": 0,
        "files": [
            {
                "title": "Antifragility",
                "path": "wiki/03_philosophies/antifragility.md",
                "level": "2_Hieu"
            },
            {
                "title": "Stoicism",
                "path": "wiki/03_philosophies/stoicism.md",
                "level": "1_Biet"
            }
        ]
    },
    "relationships": {
        "1_Biet": 0,
        "2_Quen": 1,
        "3_Than": 0,
        "4_Thuong": 0,
        "5_Yeu": 0,
        "files": [
            {
                "title": "John Doe",
                "path": "wiki/04_relationships/john-doe.md",
                "level": "2_Quen"
            }
        ]
    },
    "total_files": 5,
    "last_sync": "2026-04-12 00:03:04",
    "graph": {
        "nodes": [
            {
                "id": "deep-work",
                "title": "Deep Work",
                "group": "knowledge",
                "level": "2_Hieu",
                "path": "wiki/01_knowledge/deep-work.md"
            },
            {
                "id": "pareto-principle",
                "title": "Pareto Principle",
                "group": "principles",
                "level": "3_Hanh",
                "path": "wiki/02_principles/pareto-principle.md"
            },
            {
                "id": "antifragility",
                "title": "Antifragility",
                "group": "philosophies",
                "level": "2_Hieu",
                "path": "wiki/03_philosophies/antifragility.md"
            },
            {
                "id": "stoicism",
                "title": "Stoicism",
                "group": "philosophies",
                "level": "1_Biet",
                "path": "wiki/03_philosophies/stoicism.md"
            },
            {
                "id": "john-doe",
                "title": "John Doe",
                "group": "relationships",
                "level": "2_Quen",
                "path": "wiki/04_relationships/john-doe.md"
            }
        ],
        "links": [
            {
                "source": "pareto-principle",
                "target": "deep-work"
            },
            {
                "source": "antifragility",
                "target": "stoicism"
            },
            {
                "source": "stoicism",
                "target": "antifragility"
            },
            {
                "source": "john-doe",
                "target": "deep-work"
            },
            {
                "source": "john-doe",
                "target": "stoicism"
            }
        ]
    }
};