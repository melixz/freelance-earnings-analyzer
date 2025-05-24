from src.app.memory.session_memory import SessionMemory


def test_add_and_get_history():
    mem = SessionMemory()
    mem.add("Q1", "A1")
    mem.add("Q2", "A2")
    mem.add("Q3", "A3")
    history = mem.get_history()
    assert len(history) == 3
    assert history[-1]["question"] == "Q3"
    assert history[-1]["answer"] == "A3"


def test_history_limit():
    mem = SessionMemory()
    for i in range(10):
        mem.add(f"Q{i}", f"A{i}")
    last_five = mem.get_history(5)
    assert len(last_five) == 5
    assert last_five[0]["question"] == "Q5"
    assert last_five[-1]["answer"] == "A9"
