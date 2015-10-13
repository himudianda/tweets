from admin.web.app import run_debug


def cli(args):
    run_debug(host='0.0.0.0' if args.expose else None, port=args.port)


def init_parser(parser):
    """Initialize parser specific to the stat commands"""
    p = parser.add_parser('web', description='Web debug server')
    p.set_defaults(func=cli)

    p.add_argument('--expose', '-e', dest='expose', default=False, action='store_true', help='expose server')
    p.add_argument('--port',  '-p', dest='port', default=3000, type=int, help='port number')
