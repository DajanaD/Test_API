from app.routers.auth import router as router_auth
from app.routers.checkers import router as router_checkers
from app.routers.users import router as router_users
from app.routers.comments import router as router_comments
from app.routers.posts import router as router_posts
from app.routers.black_list import router as router_black_list

all_routers = [
    router_auth,
    router_users,
    router_comments,
    router_posts,
    router_checkers,
    router_black_list,
]
