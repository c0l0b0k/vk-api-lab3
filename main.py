import requests
import json
import sys

# Функция для получения данных пользователя
def get_user_data(user_id, token):
    url_user = f"https://api.vk.com/method/users.get?user_ids={user_id}&access_token={token}&v=5.131&lang=ru"
    response_user = requests.get(url_user)
    user_data = response_user.json()

    if 'error' in user_data:
        print("Ошибка при получении данных пользователя:", user_data['error'])
        sys.exit()

    return user_data['response'][0]  # Возвращаем информацию о пользователе

# Функция для получения подписчиков и подписок
def get_followers_and_subscriptions(user_id, token):
    url_followers = f"https://api.vk.com/method/users.getFollowers?user_id={user_id}&access_token={token}&v=5.131&lang=ru"
    url_subscriptions = f"https://api.vk.com/method/users.getSubscriptions?user_id={user_id}&access_token={token}&v=5.131&lang=ru"

    response_followers = requests.get(url_followers)
    response_subscriptions = requests.get(url_subscriptions)

    followers_data = response_followers.json()
    subscriptions_data = response_subscriptions.json()

    # Обработка подписчиков
    followers = []
    if 'response' in followers_data:
        follower_ids = followers_data['response']['items']
        # Запрос данных о подписчиках
        followers = get_user_names(follower_ids, token)

    # Обработка подписок
    users = []
    groups = []
    if 'response' in subscriptions_data:
        if 'users' in subscriptions_data['response']:
            user_ids = subscriptions_data['response']['users']['items']
            users = get_user_names(user_ids, token)
        if 'groups' in subscriptions_data['response']:
            group_ids = subscriptions_data['response']['groups']['items']
            groups = get_group_names(group_ids, token)

    return followers, users, groups

# Функция для получения имен пользователей
def get_user_names(user_ids, token):
    if not user_ids:
        return []
    user_ids_str = ",".join(map(str, user_ids))
    url = f"https://api.vk.com/method/users.get?user_ids={user_ids_str}&access_token={token}&v=5.131&lang=ru"
    response = requests.get(url)
    user_data = response.json()

    if 'error' in user_data:
        print("Ошибка при получении данных пользователей:", user_data['error'])
        return []

    users = [{'id': user['id'], 'name': f"{user['first_name']} {user['last_name']}"} for user in user_data['response']]
    return users

# Функция для получения названий групп
def get_group_names(group_ids, token):
    if not group_ids:
        return []
    group_ids_str = ",".join(map(str, group_ids))
    url = f"https://api.vk.com/method/groups.getById?group_ids={group_ids_str}&access_token={token}&v=5.131&lang=ru"
    response = requests.get(url)
    group_data = response.json()

    if 'error' in group_data:
        print("Ошибка при получении данных групп:", group_data['error'])
        return []

    groups = [{'id': group['id'], 'name': group['name']} for group in group_data['response']]
    return groups

# Функция для сохранения данных в JSON файл
def save_to_json(user_info, followers, users, groups):
    data = {
        'user_info': user_info,
        'followers': followers,
        'subscriptions': {
            'users': users,
            'groups': groups
        }
    }

    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Основная функция
def main():
    user_id = input("Введите ID пользователя ВКонтакте: ")
    token = input("Введите access token: ")

    # Получение данных пользователя
    user_info = get_user_data(user_id, token)

    # Получение подписчиков и подписок
    followers, users, groups = get_followers_and_subscriptions(user_id, token)

    # Вывод данных в консоль
    print(f"Данные пользователя {user_info['first_name']} {user_info['last_name']}:")
    print(f"Количество подписчиков: {len(followers)}")
    print(f"Количество пользователей в подписках: {len(users)}")
    print(f"Количество групп в подписках: {len(groups)}")

    # Сохранение данных в JSON-файл
    save_to_json(user_info, followers, users, groups)
    print("Данные сохранены в файл 'user_data.json'.")

# Запуск программы
if __name__ == '__main__':
    main()
