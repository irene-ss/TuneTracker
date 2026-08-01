# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  

TuneTracker 1.0 

---

## 2. Intended Use  

TuneTracker 1.0 is a simple music recommender designed for classroom exploration. It suggests songs based on a user’s preferred genre, mood, and energy level. It assumes that a listener wants songs that feel similar to a given taste profile, such as happy pop or intense rock.

---

## 3. How the Model Works  

The recommender looks at a few simple song features, including genre, mood, and energy level. It compares each song to the user’s preferred style and gives points when the song matches the requested genre or mood and when its energy is close to the target. Songs that fit better overall rise higher in the recommendation list.


---

## 4. Data  

The model uses a small catalog of 20 songs. The dataset includes a mix of genres such as pop, lofi, rock, jazz, ambient, indie pop, hip-hop, metal, and country, along with a variety of moods like happy, chill, intense, relaxed, and dreamy. No new data was added or removed for this version.

One limitation of the dataset is that it does not cover every style of music or every kind of listener preference, so it is best suited for simple, classroom-style examples rather than full real-world recommendations.

---

## 5. Strengths  

This system works well for users whose taste is fairly clear and easy to describe. It gives sensible results for profiles such as high-energy pop, calm lofi, and intense rock because those preferences are closely tied to the features the model uses.

The scoring also does a good job of matching obvious patterns, such as preferring high-energy songs for energetic profiles and lower-energy songs for calm profiles. In many cases, the recommended songs feel intuitive and easy to explain.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---
Limitations:
- It rewards exact genre and mood matches very strongly, so a user with broader tastes can get stuck seeing only very similar songs.
- The energy scoring is quite rigid. It uses an absolute energy gap and then gives no credit once the gap is large. That means a song can be unfairly ignored even if it is still a good fit for other reasons.

## 7. Evaluation  

I tested three example profiles: High-Energy Pop, Chill Lofi, and Deep Intense Rock. I looked at whether the recommendations changed in a way that matched each profile’s mood and energy.

- High-Energy Pop vs. Chill Lofi: The pop profile preferred upbeat, brighter songs with higher energy, while the lofi profile shifted toward softer, lower-energy songs with a calmer mood. This makes sense because the two profiles are asking for very different emotional experiences.
- High-Energy Pop vs. Deep Intense Rock: The pop profile favored songs that felt lively and polished, while the rock profile leaned toward songs with a stronger, more intense feel. This makes sense because the rock profile wants more force and urgency, not just a high-energy sound.
- Chill Lofi vs. Deep Intense Rock: The lofi profile chose quieter, more relaxed songs, while the rock profile picked songs that felt louder and more aggressive. This makes sense because one profile is about calm focus and the other is about intensity and drive.

---

## 8. Future Work  

I would like to improve the model by expanding the dataset to include many more styles of music, so it can better represent different listening tastes. I also want to add more user profiles to test how the system behaves for a wider range of people. In addition, I would make the algorithm more flexible so it is less likely to suggest repetitive songs and gives users a broader mix of recommendations.

---

## 9. Personal Reflection  

This project helped me understand how recommender systems work in a simple but meaningful way. I found it especially interesting to see how music apps use small signals like genre, mood, and energy to make recommendations that feel personal. I also learned that these systems can be useful, but they can also become too narrow or repetitive if they rely too heavily on a few features.
  
