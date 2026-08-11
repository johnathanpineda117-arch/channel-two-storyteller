story_profile = {
    "story": "A man survives an unexpected bear attack.",
    "type": "fiction",
    "content_pillar": "unbelievable-survival",
    "emotion": "shock-relief"
}

print("STORY PROFILE")
print("Story:", story_profile["story"])
print("Type:", story_profile["type"])
print("Pillar:", story_profile["content_pillar"])
print("Emotion:", story_profile["emotion"])

if story_profile["type"] == "nonfiction":
    print("Action: This story requires factual verification.")
else:
    print("Action: Clearly identify this story as fictional.")