import { useState, useEffect } from 'react';
import { createUser, getCurrentUser } from '../lib/api/client';

const USER_ID_KEY = 'process_miner_user_id';

export function useUser() {
    const [userId, setUserId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function initUser() {
            try {
                const storedId = localStorage.getItem(USER_ID_KEY);

                if (storedId) {
                    try {
                        // Verify existing user
                        await getCurrentUser(storedId);
                        setUserId(storedId);
                    } catch (e) {
                        console.warn('Invalid or expired user session, creating new one', e);
                        localStorage.removeItem(USER_ID_KEY);
                        await createNewUser();
                    }
                } else {
                    await createNewUser();
                }
            } catch (e) {
                console.error('Failed to initialize user', e);
            } finally {
                setIsLoading(false);
            }
        }

        async function createNewUser() {
            try {
                const user = await createUser();
                localStorage.setItem(USER_ID_KEY, user.id);
                setUserId(user.id);
            } catch (e) {
                console.error('Failed to create user', e);
            }
        }

        initUser();
    }, []);

    return { userId, isLoading };
}
