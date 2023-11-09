from app import FastAPIIngress
import ray

ray.init(
    include_dashboard=True,
    dashboard_host="0.0.0.0",
)
app = FastAPIIngress.bind()
app.name = "ad_generator"
