//
//  LWTouchDrawView.m
//  EtchTouch
//
//  Created by Evan Long on 11/14/12.
//  Copyright (c) 2012 Hippo. All rights reserved.
//

#import "LWTouchDrawView.h"

@interface LWTouchDrawView ()

@property (nonatomic, strong) NSMutableArray *points;
@property (nonatomic, strong) UIBezierPath *path;

- (void)_pan:(UIPanGestureRecognizer *)gesture;

@end

@implementation LWTouchDrawView

- (void)_setup {
    UIPanGestureRecognizer *panGesture = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(_pan:)];
    [self addGestureRecognizer:panGesture];
    [self clear];
}

- (id)initWithFrame:(CGRect)frame
{
    self = [super initWithFrame:frame];
    if (self) {
        [self _setup];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)aDecoder {
    self = [super initWithCoder:aDecoder];
    if (self) {
        [self _setup];
    }
    return self;
}

- (NSArray *)pointsDrawn {
    return self.points;
}

- (void)clear {
    self.path = [[UIBezierPath alloc] init];
    self.points = [NSMutableArray array];
    [self setNeedsDisplay];
}

#pragma mark - UIView

- (void)drawRect:(CGRect)rect {
    [self.path stroke];
}

#pragma mark - Private

- (void)_pan:(UIPanGestureRecognizer *)gesture {
    CGPoint p = [gesture locationInView:self];
    if (gesture.state == UIGestureRecognizerStateBegan) {
        if (self.path.isEmpty) {
            [self.path moveToPoint:p];
        }
        [self.points addObject:[NSValue valueWithCGPoint:p]];
        [self setNeedsDisplay];
    }
    else if (gesture.state == UIGestureRecognizerStateChanged) {
        [self.path addLineToPoint:p];
        [self.points addObject:[NSValue valueWithCGPoint:p]];
        [self setNeedsDisplay];
    }
}

@end
