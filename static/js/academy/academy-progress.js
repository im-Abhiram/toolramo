/**
 * academy-progress.js
 * Client-Side IndexedDB Storage & Progress Tracking for Ramonet Academy
 * Persists course completions, quiz attempts, and learning streaks.
 */

(function () {
    'use strict';

    const DB_NAME = 'ramonet_academy_db';
    const DB_VERSION = 1;
    let db = null;

    function openDatabase() {
        return new Promise((resolve, reject) => {
            if (db) {
                resolve(db);
                return;
            }
            const request = indexedDB.open(DB_NAME, DB_VERSION);
            request.onupgradeneeded = function (event) {
                const dbInstance = event.target.result;
                if (!dbInstance.objectStoreNames.contains('course_progress')) {
                    dbInstance.createObjectStore('course_progress', { keyPath: 'course_slug' });
                }
                if (!dbInstance.objectStoreNames.contains('quiz_results')) {
                    dbInstance.createObjectStore('quiz_results', { keyPath: 'id', autoIncrement: true });
                }
            };
            request.onsuccess = function (event) {
                db = event.target.result;
                resolve(db);
            };
            request.onerror = function (event) {
                console.error('IndexedDB open error:', event.target.errorCode);
                reject(event.target.errorCode);
            };
        });
    }

    window.saveLessonProgress = function (courseSlug, lessonId, score) {
        openDatabase().then(database => {
            const tx = database.transaction(['course_progress'], 'readwrite');
            const store = tx.objectStore('course_progress');
            const getReq = store.get(courseSlug);

            getReq.onsuccess = function () {
                let record = getReq.result;
                if (!record) {
                    record = {
                        course_slug: courseSlug,
                        completed_lessons: [lessonId],
                        scores: { [lessonId]: score || 100 },
                        updated_at: new Date().toISOString()
                    };
                } else {
                    if (!record.completed_lessons.includes(lessonId)) {
                        record.completed_lessons.push(lessonId);
                    }
                    record.scores[lessonId] = score || 100;
                    record.updated_at = new Date().toISOString();
                }
                store.put(record);
            };
        }).catch(err => console.log('Error saving progress to IndexedDB:', err));

        // Sync with server API
        fetch('/api/academy/sync-progress/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course_slug: courseSlug,
                completed_lesson_id: lessonId,
                score: score || 100
            })
        }).catch(e => console.log('Offline sync deferred.'));
    };

    window.saveQuizResult = function (lessonId, questionId, chosenAnswer, isCorrect) {
        openDatabase().then(database => {
            const tx = database.transaction(['quiz_results'], 'readwrite');
            const store = tx.objectStore('quiz_results');
            store.add({
                lesson_id: lessonId,
                question_id: questionId,
                chosen_answer: chosenAnswer,
                is_correct: isCorrect,
                timestamp: new Date().toISOString()
            });
        }).catch(err => console.log('Error saving quiz result to IndexedDB:', err));
    };

    // Update streak tracking
    document.addEventListener('DOMContentLoaded', function () {
        const lastVisit = localStorage.getItem('ramonet_academy_last_visit');
        const today = new Date().toDateString();

        if (lastVisit !== today) {
            let streak = parseInt(localStorage.getItem('ramonet_academy_streak') || '1', 10);
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);

            if (lastVisit === yesterday.toDateString()) {
                streak += 1;
            }
            localStorage.setItem('ramonet_academy_streak', streak.toString());
            localStorage.setItem('ramonet_academy_last_visit', today);

            const streakElem = document.getElementById('stat-streak');
            if (streakElem) {
                streakElem.innerHTML = `${streak} <span class="fs-6 text-muted">days</span>`;
            }
        }
    });

})();
