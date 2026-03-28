import os
import redis

r = redis.Redis.from_url(url=os.environ["REDIS_URL"])

stream = os.environ["STREAM_NAME"]
group = os.environ["GROUP_NAME"]


def main():
    try:
        # mkstream=True → creates stream if it doesn't exist
        r.xgroup_create(name=stream, groupname=group, id="0", mkstream=True)
        print(f"Group '{group}' created on stream '{stream}'")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Group already exists, skipping")
        else:
            raise


if __name__ == "__main__":
    main()
